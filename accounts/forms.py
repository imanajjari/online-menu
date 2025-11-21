from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class OwnerSignUpForm(UserCreationForm):
    username = forms.CharField(
        label="نام کاربری",
        max_length=150,
        help_text="فقط حروف لاتین، اعداد و _ مجاز است",
        widget=forms.TextInput(attrs={"placeholder": "مثال: cafe_owner"})
    )
    first_name = forms.CharField(
        label="نام",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "نام خود را وارد کنید"})
    )
    last_name = forms.CharField(
        label="نام خانوادگی",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "نام خانوادگی خود را وارد کنید"})
    )
    email = forms.EmailField(
        label="ایمیل",
        widget=forms.EmailInput(attrs={"placeholder": "example@email.com"})
    )
    password1 = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={"placeholder": "حداقل 8 کاراکتر"}),
        help_text="رمز عبور باید حداقل 8 کاراکتر باشد و شامل حروف و اعداد باشد"
    )
    password2 = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(attrs={"placeholder": "رمز عبور را دوباره وارد کنید"}),
        help_text="رمز عبور را دوباره وارد کنید"
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"input-control {classes}".strip()
            if field.required:
                field.widget.attrs["required"] = "required"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
        return user


class OwnerLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="نام کاربری",
        widget=forms.TextInput(attrs={"placeholder": "نام کاربری خود را وارد کنید", "autofocus": True})
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={"placeholder": "رمز عبور خود را وارد کنید"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"input-control {classes}".strip()

