from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

class Project(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    project_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True, related_name='managed_projects')

    is_active = models.BooleanField(default=True)

    assigned_personnel = models.ManyToManyField(settings.AUTH_USER_MODEL)
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_details', args=[str(self.id)])

class Ticket(models.Model):
    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low')
        MEDIUM = 'MEDIUM', _('Medium')
        HIGH = 'HIGH', _('High')
    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        CLOSED = 'CLOSED', _('Closed')

    class Type(models.TextChoices):
        BUG_ERROR = 'BUG/ERROR', _('Bug/Error')
        NEW_FEATURE = 'NEW FEATURE', _('New Feature')
        ENHANCEMENT = 'ENHANCEMENT', _('Ehancement')
        CHANGE  = 'CHANGE', _('Change')


    title = models.CharField(max_length=50)
    description = models.TextField()
    priority = models.CharField(max_length=50, choices=Priority.choices, blank=False)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.OPEN)
    type = models.CharField(max_length=50, choices=Type.choices, blank=False)
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(auto_now=True)
    # define one-to-many relationships for assigned user and submitter and corresponding project
    assigned_developer= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=True, null=True, related_name='assigned_tickets')
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, blank=False, related_name='submissions')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False, related_name='tickets')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('ticket_details', args=[str(self.id)])


class TicketComment(models.Model):
    """
    Stores a record of user comments for a ticket
    """
    commenter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)
    created = models.DateTimeField(default=timezone.now)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return self.message

class TicketHistory(models.Model):
    """
    Record of information each time a ticket is updated (e.g., change in status when closed)
    """
    class Action(models.TextChoices):
        ASSIGNED_TO_USER = 'ASSIGNED_TO_USER', _('Assigned to User')
        STATUS_UPDATED = 'STATUS_UPDATED', _('Status Updated')
        PRIORITY_CHANGED = 'PRIORITY_CHANGED', _('Priority Changed')

    action = models.CharField(max_length=50, choices=Action.choices)
    prev_value = models.CharField(max_length=50, null=True, blank=True)
    new_value = models.CharField(max_length=50)
    date_changed = models.DateTimeField(default=timezone.now)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='histories')


class TicketFiles(models.Model):
    """
    Stores files related to a given ticket (one-to-many)
    """
    date_uploaded = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='files')
    file = models.FileField()
    
    def __str__(self):
        return self.file.name
