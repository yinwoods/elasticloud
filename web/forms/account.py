from django import forms


class SignupForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Enter your username',
                   'pattern': '[A-z0-9]{1,30}',
                   'onchange': 'check_username();',
                   }
        )
    )
    email = forms.EmailField(
        max_length=30,
        widget=forms.EmailInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Enter your email address',
                   'onchange': 'check_email();',
                   }
        )
    )
    password = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Type a password',
                   }
        )
    )
    re_password = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Repeat your password',
                   'onchange': 'check_passwords();',
                   }
        )
    )


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Username',
                   'pattern': '[A-z0-9]{1,30}',
                   }
        )
    )
    password = forms.CharField(
        max_length=30,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Password',
                   }
        )
    )


class ForgotForm(forms.Form):
    email = forms.EmailField(
        max_length=30,
        widget=forms.EmailInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Enter your email address',
                   }
        )
    )
