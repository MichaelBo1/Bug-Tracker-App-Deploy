from django.test import TestCase
from django.core.exceptions import ValidationError
from ..validators import UpperCaseValidator, SymbolValidator

class PasswordValidatorTests(TestCase):
    def test_uppercase_on_invalid_input(self):
        """
        Validator should raise exception if password contains no uppercase letters
        """
        with self.assertRaises(ValidationError):
            UpperCaseValidator().validate(password='testc3se123%%')
    
    def test_uppercase_on_valid_input(self):
        """
        Validator should return none if password contains at least one uppercase letter
        """
        self.assertIsNone(UpperCaseValidator().validate(password='Testc3se123%%'))

    def test_symbol_on_invalid_input(self):
        """
        Validator should raise exception if password contains no special characters
        """
        with self.assertRaises(ValidationError):
            SymbolValidator().validate(password='testc3se123')
        
    def test_symbol_on_valid_input(self):
        """
        Validator should return none if password contains at least one special character
        """
        special_chars = '[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]'
        for char in special_chars:
            test_password = 'Testcase123' + char
            self.assertIsNone(UpperCaseValidator().validate(password=test_password))

    




