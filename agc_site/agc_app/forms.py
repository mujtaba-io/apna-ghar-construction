
# useless file for now.
from django import forms


class signup_form(forms.Form):
    ask_username = forms.CharField(label="Username")
    username = forms.TextInput()
    ask_password = forms.CharField(label="Password")
    password = forms.PasswordInput()
    ask_password_again = forms.CharField(label="Again Password")
    password_again = forms.PasswordInput()
    ask_are_you_a_developer = forms.CharField(label="Are you a contractor?")
    are_you_a_developer = forms.CheckboxInput()
