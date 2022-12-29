from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'email',
        ]

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'email',
        ]
        
        
class CustomUserRoleSignupForm(SignupForm):
    """Extends default allauth signup form to include selection of each user role"""
    ROLE_CHOICES = [
        ('AD', _('Administrator')),
        ('PM', _('Project Manager')),
        ('DV', _('Developer')),
        ('SM', _('Submitter'))
    ]
        
    user_role = forms.ChoiceField(choices=ROLE_CHOICES, label='Select Role To Demo')

    def save(self, request):
        user = super().save(request)
        user.user_role = self.cleaned_data['user_role']
        user.save()
        return user
    
class DemoLoginForm(forms.Form):
    demo_user = forms.ChoiceField(
        label=_('Demo User'),
        choices=[
            ('demo1', 'Demo Administrator'),
            ('demo2', 'Demo Project Manager'),
            ('demo3', 'Demo Developer'),
            ('demo4', 'Demo Submitter'),
        ]
    )


