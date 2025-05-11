# flights/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm  # Add PasswordChangeForm


class UserRegisterForm(UserCreationForm):
    # ... your existing UserRegisterForm code ...
    email = forms.EmailField(
        required=True,
        help_text="Required. A valid email address."
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text="Required."
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        help_text="Required."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already in use. Please use a different one.")
        return email


# New Form for updating user profile information (email, first name, last name)
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)  # As per our plan, these might be read-only for user
    last_name = forms.CharField(max_length=150, required=True)  # Or we can allow editing

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        # Make username read-only as it generally shouldn't be changed
        if 'username' in self.fields:
            self.fields['username'].widget.attrs['readonly'] = True
        # As per our plan, regular users can only edit email and password.
        # First name and last name are set at registration.
        # So, let's make them read-only here too for the user's own profile edit page.
        # Admins will have different capabilities.
        if 'first_name' in self.fields:
            self.fields['first_name'].widget.attrs['readonly'] = True
        if 'last_name' in self.fields:
            self.fields['last_name'].widget.attrs['readonly'] = True

    def clean_email(self):
        """
        Validate that the email is unique, excluding the current user's email.
        """
        email = self.cleaned_data.get('email')
        # self.instance is the User object being edited
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email address is already in use by another account.")
        return email

# We will use Django's built-in PasswordChangeForm directly in the view,
# but it's good to be aware of it. It handles old password, new password, and confirmation.
# No need to define it here unless you want to customize it significantly.
