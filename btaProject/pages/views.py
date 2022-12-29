from django.views import View
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from .forms import TicketFilesForm, UserRolesForm, TicketCommentForm, TicketSubmitForm, TicketUpdateForm, ProjectCreateForm, ProjectUpdateForm, ManageProjectUsersForm
from .models import Project, Ticket, TicketComment, TicketFiles


class UserAccessMixin(PermissionRequiredMixin):
    """
    Mixin to check authentication and then that the user has the required permission to view the page. Otherwise it redirects to Dashboard.
    """
    def dispatch(self, request, *args, **kwargs):
        if (not self.request.user.is_authenticated):
            # redirect user to login page if not authenticated
            return redirect_to_login(self.request.get_full_path(), self.get_login_url())
        if not self.has_permission():
            return redirect('/')
        
        return super(UserAccessMixin, self).dispatch(request, *args, **kwargs)



class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['statuses'] = Ticket.objects.values('status').annotate(count=Count('status')).order_by('-status')
        context['types'] = Ticket.objects.values('type').annotate(type_count=Count('type'))

        return context


# Accessible only by administrators
class ManageUserRolesView(UserAccessMixin, FormView):
    permission_required = 'accounts.change_user'
    model = get_user_model()
    template_name = 'manage_roles.html'
    form_class = UserRolesForm
    success_url = '/roles/'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = self.model.objects.exclude(is_superuser=True)
        return context
    
    def form_valid(self, form):
        """
        assign user roles: signal is called when user is saved to change group based on role
        """
        for user in form.cleaned_data['users']:
            user.user_role = form.cleaned_data['role']
            user.save(update_fields=['user_role'])
        return super().form_valid(form)

class MyProjectsView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'my_projects.html'
    context_object_name = 'projects'

    def get_queryset(self):
        if self.request.user.groups.filter(name='Administrator').exists():
            return self.model.objects.filter(is_active=True)

        
        elif self.request.user.groups.filter(name='Project Manager').exists():
            return self.model.objects.filter(project_manager=self.request.user, is_active=True)

        # if not admin or PM, return projects user is assigned to
        return self.request.user.project_set.filter(is_active=True)


class AboutPageView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    template_name = 'about_page.html'

class ProjectCreateView(UserAccessMixin, CreateView):
    permission_required = 'pages.add_project'
    model = Project
    success_url = '/projects/'
    template_name = 'create_project.html'
    form_class = ProjectCreateForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

        


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'project_detail.html'
    context_object_name = 'project'

    def dispatch(self, request, *args, **kwargs):
        """
         returns template if user is administrator or they are assigned to/manage the
         current project being requested
        """
        if (self.request.user.groups.filter(name='Administrator').exists() or
            self.model.objects.filter(project_manager=self.request.user).exists() or
            self.request.user.project_set.filter(pk=self.kwargs['pk']).exists()):
            return super().dispatch(request, *args, **kwargs)

        return redirect(request.META.get('HTTP_REFERER', '/'))

class ProjectUpdateView(UserAccessMixin, UpdateView):
    permission_required = 'pages.change_project'
    model = Project
    template_name = 'update_project.html'
    form_class = ProjectUpdateForm

    def dispatch(self, request, *args, **kwargs):
        # prevent editing on archived project by redirecting to detail page
        project = get_object_or_404(self.model, pk=self.kwargs['pk'])
        if not project.is_active:
            return redirect('project_details', pk=self.kwargs['pk'])
        
        return super().dispatch(request, *args, **kwargs)


class ManageProjectUsersView(UserAccessMixin, UpdateView):
    permission_required = 'pages.change_project'
    model = Project
    template_name = 'manage_project_users.html'
    form_class = ManageProjectUsersForm

    def dispatch(self, request, *args, **kwargs):
        # prevent user management on archived project by redirecting to detail page
        project = get_object_or_404(self.model, pk=self.kwargs['pk'])
        if not project.is_active:
            return redirect('project_details', pk=self.kwargs['pk'])
        
        return super().dispatch(request, *args, **kwargs)



class ArchivedProjectsView(UserAccessMixin, ListView):
    permission_required = 'pages.add_project'
    model = Project 
    template_name = 'archived_projects.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return self.model.objects.filter(is_active=False)



"""
Should show tickets that a user submitted or is assigned to
"""
class MyTicketView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'my_tickets.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        # returns all tickets if user is administrator, otherwise returns associated tickets (those assigned/submitted by user)
        if self.request.user.groups.filter(name='Administrator').exists():
            return self.model.objects.filter(status='OPEN')

        elif self.request.user.groups.filter(name__in=['Developer', 'Project Manager']).exists():
            return self.model.objects.filter(assigned_developer = self.request.user, status='OPEN')
        else:
            return self.model.objects.filter(submitter = self.request.user, status='OPEN')
# only be accessed if ticket is assigned or related to user: TODO
class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'ticket_detail.html'
    context_object_name = 'ticket'

    def dispatch(self, request, *args, **kwargs):
        # return http response if admin or developer is related to ticket. Else, redirect url
        if (self.request.user.groups.filter(name='Administrator').exists() or
           (self.model.objects.get(pk=self.kwargs['pk']).assigned_developer == self.request.user and self.request.user.user_role == 'DV') or
            (self.model.objects.get(pk=self.kwargs['pk']).submitter == self.request.user and self.request.user.user_role == 'SM')):
            return super().dispatch(request, *args, **kwargs)

        return redirect(request.META.get('HTTP_REFERER', '/'))

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['form'] = TicketCommentForm()
        return context


        

# Accessed by administrators and Project Managers
class TicketUpdateView(UserAccessMixin, UpdateView):
    permission_required = 'pages.change_ticket'
    model = Ticket
    form_class = TicketUpdateForm
    template_name = 'update_ticket.html'

    def dispatch(self, request, *args, **kwargs):
        # prevent closed ticket from being edited
        ticket = get_object_or_404(self.model, pk=self.kwargs['pk'])
        if ticket.status == 'CLOSED':
            return redirect('ticket_details', pk=self.kwargs['pk'])
        
        return super().dispatch(request, *args, **kwargs)


class TicketCommentFormView(LoginRequiredMixin, SingleObjectMixin, FormView):
    template_name = 'ticket_detail.html'
    form_class = TicketCommentForm
    model = Ticket

    def post(self, request, *args, **kwargs):
        self.object = self.get_object() # get the current ticket object
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('ticket_details', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        msg = form.cleaned_data['message']
        # Create Ticket Comment
        new_comment = TicketComment(
            commenter=self.request.user, 
            message=msg, 
            ticket=self.object)

        new_comment.save()
        return super().form_valid(form)

class TicketObjectView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'

    def get(self, request, *args, **kwargs):
        view = TicketDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = TicketCommentFormView.as_view()
        return view(request, *args, **kwargs)

class TicketSubmitView(UserAccessMixin, FormView):
    permission_required = 'pages.add_ticket'
    model = Ticket
    form_class = TicketSubmitForm
    success_url = '/tickets/'
    template_name = 'submit_ticket.html'

    
    def form_valid(self, form):
        new_ticket = Ticket(
            title=form.cleaned_data['title'],
            description=form.cleaned_data['description'],
            priority=form.cleaned_data['priority'],
            type=form.cleaned_data['type'],
            submitter=self.request.user,
            project=form.cleaned_data['project']
        )
       
        new_ticket.save()
        return super().form_valid(form)


class UploadTicketFileView(UserAccessMixin, FormView):
    permission_required = 'pages.add_ticketfiles'
    model = TicketFiles
    template_name = 'upload_ticket_file.html'
    form_class = TicketFilesForm

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse('ticket_details', kwargs={'pk': pk})

    def form_valid(self, form):
        pk = self.kwargs['pk']
        ticket = get_object_or_404(Ticket, pk=pk)
        new_file = TicketFiles(
            uploaded_by = self.request.user,
            ticket = ticket,
            file = form.cleaned_data['file']
        )
        new_file.save()
        return super().form_valid(form)

