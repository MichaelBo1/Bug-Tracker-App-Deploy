from django.urls import path
from django.views.generic.base import RedirectView
import pages.views as page_views

urlpatterns = [
    path('', page_views.DashboardView.as_view(), name='dashboard'),
    path('about', page_views.AboutPageView.as_view(), name='about'),
    path('roles/', page_views.ManageUserRolesView.as_view(), name='manage_roles'),
    path('projects/', page_views.MyProjectsView.as_view(), name='my_projects'),
    path('projects/archived', page_views.ArchivedProjectsView.as_view(), name='archived_projects'),
    path('projects/create', page_views.ProjectCreateView.as_view(), name='create_project'),
    path('projects/<int:pk>', page_views.ProjectDetailView.as_view(), name='project_details' ),
    path('projects/users/<int:pk>', page_views.ManageProjectUsersView.as_view(), name='manage_project_users'),
    path('projects/edit/<int:pk>', page_views.ProjectUpdateView.as_view(), name='update_project'),
    path('tickets/', page_views.MyTicketView.as_view(), name='my_tickets'),
    path('tickets/create', page_views.TicketSubmitView.as_view(), name='submit_ticket'),
    path('tickets/<int:pk>', page_views.TicketObjectView.as_view(), name='ticket_details'),
    path('tickets/newfile/<int:pk>', page_views.UploadTicketFileView.as_view(), name='upload_ticket_file'),
    path('tickets/edit/<int:pk>', page_views.TicketUpdateView.as_view(), name='update_ticket'),
]