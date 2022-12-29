from django.test import TestCase
from .. import factories, models


class CloseTicketsOnProjectArchiveReceiverTests(TestCase):
    fixtures = ['auth.json']

    def setUp(self):
        submitter = factories.CustomUserFactory(username='test_@submitter')
        self.project = factories.ProjectFactory(title='Test Project', description='Test Description')
        self.project.tickets.add(factories.TicketFactory(
            title='Ticket 1', 
            description='ticket desc.', 
            project=self.project, 
            submitter=submitter))
        self.project.tickets.add(factories.TicketFactory(
            title='Ticket 2', 
            description='ticket desc.', 
            project=self.project, 
            submitter=submitter))
        return super().setUp()

    def test_tickets_close_on_project_archive(self):
        """Returns true if tickets get closed when related project is archived"""
        self.project.is_active = False
        self.project.save()
        for ticket in self.project.tickets.all():
            self.assertEqual(ticket.status, 'CLOSED')
        

    def test_tickets_dont_change_if_project_is_not_archived(self):
        """Returns true if tickets remain open if project is saved but not archived"""
        self.project.title = 'Updated Test Project Title'
        self.project.save()
        for ticket in self.project.tickets.all():
                self.assertEqual(ticket.status, models.Ticket.Status.OPEN)


class RecordTicketHistoryReceiverTests(TestCase):
    fixtures = ['auth.json']
    def setUp(self):
        submitter = factories.CustomUserFactory(username='test_@submitter')
        project = factories.ProjectFactory(title='Test Project', description='Test Description')
        self.ticket = factories.TicketFactory(
            title='Test Ticket', 
            description='ticket desc.', 
            project=project, 
            submitter=submitter)
        return super().setUp()

    def test_no_history_added_if_ticket_is_created(self):
        """Returns true if no history is recorded on ticket creation"""
        self.assertFalse(self.ticket.histories.all().exists())

    def test_no_history_added_if_ticket_has_not_changed(self):
        """Returns true if no history is recorded when ticket updates without changing recorded fields"""
        self.ticket.title = 'Updated Ticket Title'
        self.ticket.save()
        self.assertFalse(self.ticket.histories.all().exists())
    
    def test_history_added_when_developer_changed(self):
        """Returns true if history is recorded when assigned developer changes"""
        dev = factories.CustomUserFactory(username='test_@dev')
        self.ticket.assigned_developer = dev
        self.ticket.save()
        self.assertTrue(self.ticket.histories.all().exists())


    def test_no_history_added_if_status_has_not_changed(self):
        """Returns true if no history is recorded when ticket updates without changing status"""
        self.ticket.status = models.Ticket.Status.OPEN
        self.ticket.save()
        self.assertFalse(self.ticket.histories.all().exists())

    def test_history_added_when_status_updated(self):
        """Returns true if history is recorded when status is updated"""
        self.ticket.status = models.Ticket.Status.CLOSED
        self.ticket.save()
        self.assertTrue(self.ticket.histories.all().exists())

    def test_no_history_added_if_priority_has_not_changed(self):
        """Returns true if no history is recorded when ticket updates without changing priority"""
        self.ticket.priority = models.Ticket.Priority.MEDIUM
        self.ticket.save()
        self.assertFalse(self.ticket.histories.all().exists())

    def test_history_added_when_priority_changed(self):
        """Returns true if history is recorded when priority changes"""
        self.ticket.priority = models.Ticket.Priority.HIGH
        self.ticket.save()
        self.assertTrue(self.ticket.histories.all().exists())

    def test_history_added_when_type_changed(self):
        """Returns true if history is recorded when ticket type changes"""
        self.ticket.type = models.Ticket.Type.CHANGE