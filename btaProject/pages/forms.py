from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import Project, Ticket, TicketComment, TicketFiles


ROLES = [
    ('AD', 'Administrator'),
    ('PM', 'Project Manager'),
    ('DV', 'Developer'),
    ('SM', 'Submitter')
]


class UserRolesForm(forms.Form):
    """
    Form to select multiple users and assign them a given role
    """
    users = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.exclude(is_superuser=True))
    # TODO: change this. Ideally it should query the user model and not be hard coded
    role = forms.ChoiceField(choices=ROLES)


class TicketCommentForm(ModelForm):
    class Meta:
        model = TicketComment
        fields = ['message']


class TicketSubmitForm(ModelForm):
    class Meta:
        model = Ticket
        fields = [
        'title',
        'description',
        'project',
        'priority',
        'status',
        'type'
    ]


class TicketUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        """
        Changes queryset to only show developers that can be assigned a ticket
        """
        super(TicketUpdateForm, self).__init__(*args, **kwargs)
        self.fields['assigned_developer'].queryset = get_user_model().objects.filter(is_superuser=False, user_role='DV')

    class Meta:
        model = Ticket
        fields = [
        'title',
        'description',
        'assigned_developer',
        'priority',
        'status',
        'type'
    ]


class ProjectCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        """
        Changes queryset to only allow non-admin users (and not the current user) to be assigned to project
        """
        self.user = kwargs.pop('user')
        super(ProjectCreateForm, self).__init__(*args, **kwargs)
        self.fields['project_manager'].queryset = get_user_model().objects.filter(user_role='PM')
        self.fields['assigned_personnel'].queryset = get_user_model().objects.exclude(Q(is_superuser=True) | Q(user_role__in=['AD', 'PM']) | Q(pk=self.user.pk))

    class Meta:
        model = Project
        exclude = ['is_active']


        
class ProjectUpdateForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'is_active'
        ]
        labels = {
            'is_active': _('Active')
        }

class ManageProjectUsersForm(ModelForm):
    
    class Meta: 
        model = Project
        fields = ['assigned_personnel', 'project_manager']
    def __init__(self, *args, **kwargs):
        super(ManageProjectUsersForm, self).__init__(*args, **kwargs)
        self.fields['assigned_personnel'].queryset = get_user_model().objects.exclude(Q(is_superuser=True) | Q(user_role__in=['AD', 'PM']))
        self.fields['project_manager'].queryset = get_user_model().objects.filter(user_role='PM')


class TicketFilesForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(TicketFilesForm, self).__init__(*args, **kwargs)
        self.fields['ticket'].queryset = Ticket.objects.filter(status='OPEN')
    class Meta:
        model = TicketFiles
        exclude = ['date_uploaded', 'uploaded_by']