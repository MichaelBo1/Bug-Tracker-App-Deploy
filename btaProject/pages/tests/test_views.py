import factory
from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from allauth.account.models import EmailAddress
from .. import factories
from .. import views

class LoginSharedTestsMixin:
    """
    Includes standard tests for views requiring login to access.
    """
    view = None
    name = ''
    url = ''
    template = ''
    factory = RequestFactory()

    def get_response(self, method, route, is_url=True):
        # returns the response after generating a request
        if is_url:
            request = getattr(self.factory, method)(route)
        else:
            request = getattr(self.factory, method)(reverse(route))
        request.user = self.user

        return self.view.as_view()(request)

    def test_page_loads_correctly_from_url(self):
        response = self.get_response('get', self.url)
        self.assertEqual(response.status_code, 200)

    def test_page_loads_correctly_from_name(self):
        response = self.get_response('get', self.name, is_url=False)
        self.assertEqual(response.status_code, 200)

    def test_valid_request_renders_correct_template(self):
        response = self.client.get(reverse(self.name))
        self.assertTemplateUsed(response, self.template)


class PermissionSharedTestsMixin:
    """
    Includes standard tests for views requiring a specific permission to access.
    """
    view = None
    name = ''
    url = ''
    template = ''
    permission_model = None
    permission_codename = ''
    factory = RequestFactory()

    def set_user_permission(self):
        content_type = ContentType.objects.get_for_model(self.permission_model)
        self.user.user_permissions.add(Permission.objects.get(content_type=content_type, codename=self.permission_codename))
        self.user.save()

    def get_response(self, method, route, is_url=True):
        # returns the response after generating a request
        if is_url:
            request = getattr(self.factory, method)(route)
        else:
            request = getattr(self.factory, method)(reverse(route))
        request.user = self.user

        return self.view.as_view()(request)
    
    def test_page_loads_correctly_from_url_with_permission(self):
        self.set_user_permission()
        response = self.get_response('get', self.url)
        self.assertEqual(response.status_code, 200)

    def test_page_loads_correctly_from_name_with_permission(self):
        self.set_user_permission()
        response = self.get_response('get', self.name, is_url=False)
        self.assertEqual(response.status_code, 200)

    def test_valid_request_renders_correct_template_with_permission(self):
        self.set_user_permission()
        response = self.client.get(reverse(self.name))
        self.assertTemplateUsed(response, self.template)
    
    def test_redirects_without_permission(self):
        response = self.get_response('get', self.name, is_url=False)        
        self.assertEqual(response.status_code, 302)


class ProjectPKSharedTestsMixin:
    """
    Includes standard tests for views requiring a specific project PK to acccess
    """
    view = None
    name = ''
    url = ''
    template = ''
    permission_name = ''
    permission_codename = ''
    factory = RequestFactory()

    def set_user_permission(self):
        content_type = factories.ContentTypeFactory(app_label='pages', model='project')
        project_perm = factories.PermissionFactory(name=self.permission_name, codename=self.permission_codename, content_type=content_type)
        self.user.user_permissions.add(project_perm)
        self.user.save()

    def get_response(self):
        kwargs = {'pk': str(self.project.pk)}
        request = self.factory.get(self.url)
        request.user = self.user
        return self.view.as_view()(request, **kwargs)

    def test_page_loads_if_project_is_active_with_permission(self):
        """Returns true if page loads when project is active"""
        self.set_user_permission()
        response = self.get_response()
        self.assertEqual(response.status_code, 200)

    def test_page_redirects_if_project_is_not_active_with_permission(self):
        """Returns true if page redirects when project is not active"""
        self.set_user_permission()
        self.project.is_active = False
        self.project.save()
        response = self.get_response()
        self.assertEqual(response.status_code, 302)

    def test_page_redirects_if_user_is_not_permitted(self):
        """Returns true if user is not permitted and so is redirected"""
        response = self.get_response()
        self.assertEqual(response.status_code, 302)

    

class ValidUserTestCase(TestCase):
    """
    Standard test case that creates a valid user that is logged in to test the views.
    """
    fixtures = ['auth.json']
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(username="@testself.user")
        cls.user.set_password("Testing123%")
        cls.user.save()
        EmailAddress.objects.create(
            user=cls.user,
            email="test.self.user@example.com",
            primary=True,
            verified=True,
        )
        return super().setUpTestData()

    def setUp(self):
        self.client.force_login(self.user)
        return super().setUp()


"""LOGIN REQUIRED VIEWS TESTS"""
class DashboardViewTests(LoginSharedTestsMixin, ValidUserTestCase):
    view = views.DashboardView
    name = 'dashboard'
    url = '/'
    template = 'dashboard.html'

    def test_context_data_exists_when_page_loads(self):
        """Returns true if context_data correctly loads"""
        response = self.get_response(method='get', route=self.name, is_url=False)
        self.assertIsNotNone(response.context_data['statuses'])
        self.assertIsNotNone(response.context_data['types'])

class MyProjectsViewTests(LoginSharedTestsMixin, ValidUserTestCase):
    view = views.MyProjectsView
    name = 'my_projects'
    url = 'projects/'
    template = 'my_projects.html'
    
class AboutPageViewTests(LoginSharedTestsMixin, ValidUserTestCase):
    view = views.AboutPageView
    name = 'about'
    url = 'about/'
    template = 'about_page.html'


class ProjectDetailViewTests(ValidUserTestCase):
    view = views.ProjectDetailView
    name = 'project_details'
    url = 'projects/'
    template = 'project_detail.html'
    factory = RequestFactory()

    def setUp(self):
        self.project = factories.ProjectFactory(title='Test Project', description='Test Project Description')
        return super().setUp()

    def get_response(self):
        kwargs = {'pk': str(self.project.pk)}
        request = self.factory.get(self.url)
        request.user = self.user
        return self.view.as_view()(request, **kwargs)

    def test_page_loads_correctly_if_user_is_administrator(self):
        """Returns true if page loads when user is Administrator"""
        # Setup group
        admin_group = factories.GroupFactory(name='Administrator')
        self.user.groups.add(admin_group)

        response = self.get_response()
        self.assertEqual(response.status_code, 200)

    def test_page_loads_correctly_if_user_is_current_PM(self):
        "Returns true if page loads when user is the assigned project manager"
        # Set user as current project's manager
        self.project.project_manager = self.user
        self.project.save()

        response = self.get_response()
        self.assertEqual(response.status_code, 200)

    def test_page_loads_correctly_if_user_is_assigned_to_project(self):
        """Returns true if user is currently assigned to project"""
        self.user.project_set.add(self.project)
        self.user.save()

        response = self.get_response()
        self.assertEqual(response.status_code, 200)

    def test_page_redirects_if_user_is_not_permitted(self):
        """Returns true if user is not one of the above and so is redirected"""
        response = self.get_response()
        self.assertEqual(response.status_code, 302)


        

class MyTicketViewTests(LoginSharedTestsMixin, ValidUserTestCase):
    view = views.MyTicketView
    name = 'my_tickets'
    url = 'tickets/'
    template = 'my_tickets.html'

class TicketDetailViewTests(ValidUserTestCase):
    view = views.TicketDetailView
    name = 'ticket_details'
    url = 'tickets/'
    template = 'ticket_details.html'
    factory = RequestFactory()

    def create_ticket_from_user(self, submitter):
        ticket = factories.TicketFactory(
            title='Test Ticket', 
            description='Test Ticket Description',
            submitter=submitter,
            project=factories.ProjectFactory(title='Test Project', description='Test Project Description'))
        return ticket
        

    def get_response(self, ticket):
        kwargs = {'pk': str(ticket.pk)}
        request = self.factory.get(self.url)
        request.user = self.user
        return self.view.as_view()(request, **kwargs)

    def test_page_loads_correctly_if_user_is_administrator(self):
        """Returns true if page loads when user is Administrator"""
        submitter = factories.CustomUserFactory(username='test_submitter')
        ticket = self.create_ticket_from_user(submitter=submitter)
        # Setup group
        admin_group = factories.GroupFactory(name='Administrator')
        self.user.groups.add(admin_group)

        response = self.get_response(ticket=ticket)
        self.assertEqual(response.status_code, 200)

    def test_page_loads_correctly_if_user_is_ticket_submitter(self):
        "Returns true if page loads when user is the ticket submitter"
        ticket = self.create_ticket_from_user(submitter=self.user)

        response = self.get_response(ticket=ticket)
        self.assertEqual(response.status_code, 200)

    def test_page_redirects_if_user_is_not_developer_and_assigned_to_ticket(self):
        """Returns true if page redirects if user is not developer and assigned to the ticket"""
        submitter = factories.CustomUserFactory(username='test_submitter')
        ticket = self.create_ticket_from_user(submitter=submitter)
        ticket.assigned_developer = self.user
        ticket.save()

        response = self.get_response(ticket=ticket)
        self.assertEqual(response.status_code, 302)

    def test_page_loads_correctly_if_user_is_developer_and_assigned_to_ticket(self):
        """Returns true if page laods if user is developer and assigned to the ticket"""
        submitter = factories.CustomUserFactory(username='test_submitter')
        ticket = self.create_ticket_from_user(submitter=submitter)
        ticket.assigned_developer = self.user
        ticket.save()

        self.user.user_role = 'DV'
        self.user.save()

        response = self.get_response(ticket=ticket)
        self.assertEqual(response.status_code, 200)


    def test_page_redirects_if_user_is_not_permitted(self):
        """Returns true if user is not one of the above and so is redirected"""
        submitter = factories.CustomUserFactory(username='test_submitter')
        ticket = self.create_ticket_from_user(submitter=submitter)
        response = self.get_response(ticket=ticket)
        self.assertEqual(response.status_code, 302)
    
"""PERMISSION-RESTRICTED VIEWS TESTS"""
class ManageUserRolesViewTests(PermissionSharedTestsMixin, ValidUserTestCase):
    view = views.ManageUserRolesView
    name = 'manage_roles'
    url = 'roles/'
    template = 'manage_roles.html'
    permission_model = get_user_model()
    permission_codename = 'change_customuser'

    def test_correctly_loads_context_data_with_permission(self):
        """Returns true if context includes users, excluding superusers"""
        self.set_user_permission()
        response = self.get_response('get', self.name, is_url=False)
        self.assertQuerysetEqual(response.context_data['users'], get_user_model().objects.exclude(is_superuser=True))

class ProjectCreateViewTests(PermissionSharedTestsMixin, ValidUserTestCase):
    view = views.ProjectCreateView
    name = 'create_project'
    url = 'projects/create/'
    template = 'create_project.html'

    def set_user_permission(self):
        content_type = factories.ContentTypeFactory(app_label='pages', model='project')
        add_project_perm = factories.PermissionFactory(name='User can add project', codename='add_project', content_type=content_type)
        self.user.user_permissions.add(add_project_perm)
        self.user.save()

    
class ProjectUpdateViewTests(ProjectPKSharedTestsMixin, ValidUserTestCase):
    view = views.ProjectUpdateView
    name = 'update_project'
    url = 'projects/edit'
    template = 'update_project.html'
    permission_name = 'User can change project'
    permission_codename = 'change_project'

    def setUp(self):
        self.project = factories.ProjectFactory(title='Test Project', description='Test Project Description')
        return super().setUp()


class ManageProjectUsersViewTests(ProjectPKSharedTestsMixin, ValidUserTestCase):
    view = views.ManageProjectUsersView
    name = 'manage_project_users'
    url = 'projects/users'
    template = 'manage_project_users.html'
    permission_name = 'User can change project'
    permission_codename = 'change_project'

    def setUp(self):
        self.project = factories.ProjectFactory(title='Test Project', description='Test Project Description')
        return super().setUp()

class ArchivedProjectsViewTests(PermissionSharedTestsMixin, ValidUserTestCase):
    view = views.ProjectCreateView
    name = 'archived_projects'
    url = 'projects/archived'
    template = 'archived_projects.html'

    def set_user_permission(self):
        content_type = factories.ContentTypeFactory(app_label='pages', model='project')
        add_project_perm = factories.PermissionFactory(name='User can add project', codename='add_project', content_type=content_type)
        self.user.user_permissions.add(add_project_perm)
        self.user.save()
    

class TicketSubmitViewTests(PermissionSharedTestsMixin, ValidUserTestCase):
    view = views.TicketSubmitView
    name = 'submit_ticket'
    url = 'tickets/create'
    template = 'submit_ticket.html'
    def set_user_permission(self):
        content_type = factories.ContentTypeFactory(app_label='pages', model='ticket')
        add_ticket_perm = factories.PermissionFactory(name='User can add ticket', codename='add_ticket', content_type=content_type)
        self.user.user_permissions.add(add_ticket_perm)
        self.user.save()

    def test_valid_form_creates_ticket(self):
        self.set_user_permission()
        project = factories.ProjectFactory(title='Test Project', description='Test Project Description')
        valid_form_data = {
                    'title': 'Test Ticket Unique',
                    'description': 'Test Description...',
                    'project': project,
                    'priority': 'HIGH',
                    'status': 'OPEN',
                    'type': 'ENHANCEMENT'
        }
        request = self.factory.post(reverse(self.name), data=valid_form_data)
        request.user = self.user
        response = self.view.as_view()(request)
        self.assertEqual(response.status_code, 200)
        
 
class TicketUpdateViewTests(ValidUserTestCase):
    view = views.TicketUpdateView
    name = 'update_ticket'
    url = 'tickets/edit'
    template = 'update_ticket.html'
    factory = RequestFactory()
    def setUp(self):
        user = factories.CustomUserFactory(username='test_ticket_user')
        self.ticket = factories.TicketFactory(
            title='Test Ticket', 
            description='Test Ticket Description',
            submitter=user,
            project=factories.ProjectFactory(title='Test Project', description='Test Project Description'))
        return super().setUp()

    def set_user_permission(self):
        content_type = factories.ContentTypeFactory(app_label='pages', model='ticket')
        change_ticket_perm = factories.PermissionFactory(name='User can change ticket', codename='change_ticket', content_type=content_type)
        self.user.user_permissions.add(change_ticket_perm)
        self.user.save()

    
    def get_response(self):
        kwargs = {'pk': str(self.ticket.pk)}
        request = self.factory.get(self.url)
        request.user = self.user
        return self.view.as_view()(request, **kwargs)
    
    def test_page_loads_if_ticket_is_open_with_permission(self):
        """Returns true if page loads when ticket is open"""
        self.set_user_permission()
        response = self.get_response()
        self.assertEqual(response.status_code, 200)

    def test_page_redirects_if_ticket_is_closed_with_permission(self):
        """Returns true if page redirects when ticket is closed"""
        self.set_user_permission()
        self.ticket.status = 'CLOSED'
        self.ticket.save()
        response = self.get_response()
        self.assertEqual(response.status_code, 302)

    def test_page_redirects_if_user_is_not_permitted(self):
        response = self.get_response()
        self.assertEqual(response.status_code, 302)



class UploadTicketFileView(PermissionSharedTestsMixin, ValidUserTestCase):
    view = views.UploadTicketFileView
    name = 'upload_ticket_file'
    url = 'tickets/newfile'
    template = 'upload_ticket_file.html'


    def set_user_permission(self):
        content_type = factories.ContentTypeFactory(app_label='pages', model='ticketfiles')
        add_file_perm = factories.PermissionFactory(name='User can add ticketfiles', codename='add_ticketfiles', content_type=content_type)
        self.user.user_permissions.add(add_file_perm)
        self.user.save()


        

