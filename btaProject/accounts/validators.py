import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class UpperCaseValidator:  
    """
    Raises error if there is not at least one uppercase letter in the password
    """
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _('This password must contain at least one uppercase letter.'),
                code='does_not_contain_uppercase'
            )
        
    def get_help_text(self):
        return _(
            'Your password must contain at least one uppercase letter.'
        )


class SymbolValidator:
    """
    Raises error if there is not at least one special symbol in the password
    """
    def validate(self, password, user=None):
        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
                        raise ValidationError(
                _('This password must contain at least one special character.'),
                code='does_not_contain_symbol'
            )
        
    def get_help_text(self):
        return _(
            'Your password must contain at least one special character.'
        )



