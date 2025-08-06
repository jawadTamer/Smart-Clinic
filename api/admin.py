from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import User, Doctor, Patient, Clinic, DoctorSchedule, Appointment
from django.db import IntegrityError


# -------------------------------
# Base User Creation Form
# -------------------------------
class BaseUserForm(UserCreationForm):
    """Base form with common user fields and validation"""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username", "email", "first_name", "last_name", "phone", "address",
            "date_of_birth", "gender", "profile_picture", "is_active"
        )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError(f"Username '{username}' is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError(f"Email '{email}' is already registered.")
        return email


# -------------------------------
# Doctor Creation Form (with User creation)
# -------------------------------
class DoctorForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255, required=False)
    date_of_birth = forms.DateField(required=False)
    gender = forms.ChoiceField(choices=User.GENDER_CHOICES, required=False)
    profile_picture = forms.ImageField(required=False)
    is_active = forms.BooleanField(initial=True, required=False)
    password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Doctor
        fields = [
            "specialization", "license_number", "clinic",
            "experience_years", "consultation_fee", "bio", "is_available"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and getattr(self.instance, "user_id", None):
            self.fields["username"].initial = self.instance.user.username
            self.fields["email"].initial = self.instance.user.email
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["phone"].initial = self.instance.user.phone
            self.fields["address"].initial = self.instance.user.address
            self.fields["date_of_birth"].initial = self.instance.user.date_of_birth
            self.fields["gender"].initial = self.instance.user.gender
            self.fields["profile_picture"].initial = self.instance.user.profile_picture
            self.fields["is_active"].initial = self.instance.user.is_active

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if not self.instance.pk and (not password1 or not password2):
            raise ValidationError("Password is required for new doctor.")

        if password1 != password2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username__iexact=username)
        if self.instance.pk and getattr(self.instance, "user_id", None):
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            qs = User.objects.filter(email__iexact=email)
            if self.instance.pk and getattr(self.instance, "user_id", None):
                qs = qs.exclude(pk=self.instance.user.pk)
            if qs.exists():
                raise ValidationError("This email is already registered.")
        return email

    def clean_license_number(self):
        license_number = self.cleaned_data.get("license_number")
        qs = Doctor.objects.filter(license_number=license_number)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("This license number is already registered.")
        return license_number

    @transaction.atomic
    def save(self, commit=True):
        doctor = super().save(commit=False)

        if self.instance.pk and getattr(self.instance, "user_id", None):
            user = self.instance.user
            user.username = self.cleaned_data["username"]
            user.email = self.cleaned_data.get("email")
            user.first_name = self.cleaned_data.get("first_name")
            user.last_name = self.cleaned_data.get("last_name")
            user.phone = self.cleaned_data.get("phone")
            user.address = self.cleaned_data.get("address")
            user.date_of_birth = self.cleaned_data.get("date_of_birth")
            user.gender = self.cleaned_data.get("gender")
            user.profile_picture = self.cleaned_data.get("profile_picture")
            user.is_active = self.cleaned_data.get("is_active", True)

            if self.cleaned_data.get("password1"):
                user.set_password(self.cleaned_data["password1"])
            user.save()
        else:
            user = User.objects.create_user(
                username=self.cleaned_data["username"],
                email=self.cleaned_data.get("email"),
                first_name=self.cleaned_data.get("first_name"),
                last_name=self.cleaned_data.get("last_name"),
                user_type="doctor",
                phone=self.cleaned_data.get("phone"),
                address=self.cleaned_data.get("address"),
                date_of_birth=self.cleaned_data.get("date_of_birth"),
                gender=self.cleaned_data.get("gender"),
                profile_picture=self.cleaned_data.get("profile_picture"),
                is_active=self.cleaned_data.get("is_active", True),
                password=self.cleaned_data["password1"],
            )

        doctor.user = user
        if commit:
            doctor.save()
        return doctor


# -------------------------------
# Patient Creation Form (with User creation)
# -------------------------------
class PatientForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(max_length=255, required=False)
    date_of_birth = forms.DateField(required=False)
    gender = forms.ChoiceField(choices=User.GENDER_CHOICES, required=False)
    profile_picture = forms.ImageField(required=False)
    is_active = forms.BooleanField(initial=True, required=False)
    password1 = forms.CharField(widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Patient
        fields = ["medical_history"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and getattr(self.instance, "user_id", None):
            self.fields["username"].initial = self.instance.user.username
            self.fields["email"].initial = self.instance.user.email
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["phone"].initial = self.instance.user.phone
            self.fields["address"].initial = self.instance.user.address
            self.fields["date_of_birth"].initial = self.instance.user.date_of_birth
            self.fields["gender"].initial = self.instance.user.gender
            self.fields["profile_picture"].initial = self.instance.user.profile_picture
            self.fields["is_active"].initial = self.instance.user.is_active

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if not self.instance.pk and (not password1 or not password2):
            raise ValidationError("Password is required for new patient.")

        if password1 != password2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username__iexact=username)
        if self.instance.pk and getattr(self.instance, "user_id", None):
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            qs = User.objects.filter(email__iexact=email)
            if self.instance.pk and getattr(self.instance, "user_id", None):
                qs = qs.exclude(pk=self.instance.user.pk)
            if qs.exists():
                raise ValidationError("This email is already registered.")
        return email

    @transaction.atomic
    def save(self, commit=True):
        patient = super().save(commit=False)

        if self.instance.pk and getattr(self.instance, "user_id", None):
            user = self.instance.user
            user.username = self.cleaned_data["username"]
            user.email = self.cleaned_data.get("email")
            user.first_name = self.cleaned_data.get("first_name")
            user.last_name = self.cleaned_data.get("last_name")
            user.phone = self.cleaned_data.get("phone")
            user.address = self.cleaned_data.get("address")
            user.date_of_birth = self.cleaned_data.get("date_of_birth")
            user.gender = self.cleaned_data.get("gender")
            user.profile_picture = self.cleaned_data.get("profile_picture")
            user.is_active = self.cleaned_data.get("is_active", True)

            if self.cleaned_data.get("password1"):
                user.set_password(self.cleaned_data["password1"])
            user.save()
        else:
            user = User.objects.create_user(
                username=self.cleaned_data["username"],
                email=self.cleaned_data.get("email"),
                first_name=self.cleaned_data.get("first_name"),
                last_name=self.cleaned_data.get("last_name"),
                user_type="patient",
                phone=self.cleaned_data.get("phone"),
                address=self.cleaned_data.get("address"),
                date_of_birth=self.cleaned_data.get("date_of_birth"),
                gender=self.cleaned_data.get("gender"),
                profile_picture=self.cleaned_data.get("profile_picture"),
                is_active=self.cleaned_data.get("is_active", True),
                password=self.cleaned_data["password1"],
            )

        patient.user = user
        if commit:
            patient.save()
        return patient


# -------------------------------
# Admin Classes
# -------------------------------
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "first_name", "last_name", "user_type", "is_active", "created_at"]
    list_filter = ["user_type", "is_active", "gender", "created_at"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["-created_at"]


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    form = DoctorForm
    list_display = ["user", "specialization", "license_number", "clinic", "experience_years", "is_available"]
    list_filter = ["specialization", "is_available", "clinic", "created_at"]
    search_fields = ["user__username", "user__first_name", "user__last_name", "license_number"]
    ordering = ["user__first_name"]

    def save_model(self, request, obj, form, change):
        try:
            with transaction.atomic():
                form.save(commit=True)
        except IntegrityError:
            raise forms.ValidationError("Username or email already exists. Please choose another.")
        except ValidationError as e:
            raise e
        except Exception as e:
            raise forms.ValidationError(f"Failed to save doctor: {str(e)}")


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    form = PatientForm
    list_display = ["user", "medical_history", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "user__first_name", "user__last_name"]
    ordering = ["user__first_name"]

    def save_model(self, request, obj, form, change):
        try:
            with transaction.atomic():
                form.save(commit=True)
        except IntegrityError:
            raise forms.ValidationError("Username or email already exists. Please choose another.")
        except ValidationError as e:
            raise e
        except Exception as e:
            raise forms.ValidationError(f"Failed to save patient: {str(e)}")


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "email", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "address", "phone", "email"]
    ordering = ["name"]


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ["doctor", "day", "start_time", "end_time", "is_available"]
    list_filter = ["day", "is_available", "doctor__specialization"]
    search_fields = ["doctor__user__first_name", "doctor__user__last_name"]
    ordering = ["doctor__user__first_name", "day"]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ["patient", "doctor", "appointment_date", "appointment_time", "status", "created_at"]
    list_filter = ["status", "appointment_date", "doctor__specialization", "created_at"]
    search_fields = [
        "patient__user__first_name", "patient__user__last_name",
        "doctor__user__first_name", "doctor__user__last_name"
    ]
    ordering = ["-appointment_date", "-appointment_time"]
    date_hierarchy = "appointment_date"
