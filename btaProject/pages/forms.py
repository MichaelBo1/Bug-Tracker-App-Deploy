from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import Project, Ticket, TicketComment, TicketFiles
from accounts.models import CustomUser

ROLES = [
    (CustomUser.Roles.ADMINISTRATOR, 'Administrator'),
    (CustomUser.Roles.PROJECT_MANAGER, 'Project Manager'),
    (CustomUser.Roles.DEVELOPER, 'Developer'),
    (CustomUser.Roles.SUBMITTER, 'Submitter')
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
        self.fields['assigned_developer'].queryset = get_user_model().objects.filter(is_superuser=False, user_role=CustomUser.Roles.DEVELOPER)

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
        self.fields['project_manager'].queryset = get_user_model().objects.filter(user_role=CustomUser.Roles.PROJECT_MANAGER)
        self.fields['assigned_personnel'].queryset = get_user_model().objects.exclude(Q(is_superuser=True) | Q(user_role__in=[CustomUser.Roles.ADMINISTRATOR, CustomUser.Roles.PROJECT_MANAGER]) | Q(pk=self.user.pk))

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
        self.fields['assigned_personnel'].queryset = get_user_model().objects.exclude(Q(is_superuser=True) | Q(user_role__in=[CustomUser.Roles.ADMINISTRATOR, CustomUser.Roles.PROJECT_MANAGER]))
        self.fields['project_manager'].queryset = get_user_model().objects.filter(user_role=CustomUser.Roles.PROJECT_MANAGER)


class TicketFilesForm(ModelForm):
    class Meta:
        model = TicketFiles
        fields = ['file']