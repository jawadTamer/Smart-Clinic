from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import User, Doctor, Patient, Clinic, DoctorSchedule, Appointment


# -------------------------------
# SPECIALIZATION Choices
# -------------------------------
SPECIALIZATION_CHOICES = (
    ("Cardiology", "Cardiology"),
    ("Dermatology", "Dermatology"),
    ("Neurology", "Neurology"),
    ("Orthopedics", "Orthopedics"),
    ("Pediatrics", "Pediatrics"),
    ("Psychiatry", "Psychiatry"),
    ("General", "General Medicine"),
    ("Dental", "Dental"),
    ("Eye", "Eye Care"),
    ("Surgery", "Surgery"),
)


# -------------------------------
# Base User Form
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
# Doctor Form
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

    specialization = forms.ChoiceField(choices=SPECIALIZATION_CHOICES, required=True)

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
# Patient Form
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
        fields = ["medical_history", "allergies", "blood_type", "emergency_contact_name", "emergency_contact"]

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
# DoctorSchedule Form
# -------------------------------
class DoctorScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = ["schedule_type", "day", "specific_date", "start_time", "end_time", "is_available", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add some help text
        self.fields["schedule_type"].help_text = "Choose 'Recurring Weekly' for regular weekly schedule or 'Specific Date' for one-time availability"
        self.fields["day"].help_text = "Only required for recurring schedules"
        self.fields["specific_date"].help_text = "Only required for specific date schedules"

    def clean(self):
        cleaned_data = super().clean()
        schedule_type = cleaned_data.get("schedule_type")
        day = cleaned_data.get("day")
        specific_date = cleaned_data.get("specific_date")

        if schedule_type == "recurring":
            if not day:
                self.add_error("day", "Day is required for recurring schedules.")
            if specific_date:
                self.add_error("specific_date", "Specific date should not be set for recurring schedules.")
        elif schedule_type == "specific":
            if not specific_date:
                self.add_error("specific_date", "Specific date is required for specific date schedules.")
            if day:
                self.add_error("day", "Day should not be set for specific date schedules.")

        return cleaned_data


# -------------------------------
# Admin Registration
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


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    form = PatientForm
    list_display = ["user", "blood_type", "emergency_contact_name", "emergency_contact", "created_at"]
    list_filter = ["blood_type", "created_at"]
    search_fields = ["user__username", "user__first_name", "user__last_name"]
    ordering = ["user__first_name"]


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "email", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "address", "phone", "email"]
    ordering = ["name"]


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    form = DoctorScheduleForm
    list_display = ["doctor", "schedule_type", "day", "specific_date", "start_time", "end_time", "is_available"]
    list_filter = ["schedule_type", "day", "is_available", "doctor__specialization", "specific_date"]
    search_fields = ["doctor__user__first_name", "doctor__user__last_name"]
    ordering = ["doctor__user__first_name", "schedule_type", "day", "specific_date"]
    
    fieldsets = (
        ("Doctor", {
            "fields": ("doctor",)
        }),
        ("Schedule Type", {
            "fields": ("schedule_type",),
            "description": "Choose between recurring weekly schedule or specific date schedule"
        }),
        ("Recurring Schedule", {
            "fields": ("day",),
            "description": "For weekly recurring schedules only"
        }),
        ("Specific Date Schedule", {
            "fields": ("specific_date",),
            "description": "For one-time or specific date schedules only"
        }),
        ("Time & Availability", {
            "fields": ("start_time", "end_time", "is_available")
        }),
        ("Additional Info", {
            "fields": ("notes",),
            "classes": ("collapse",)
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('doctor__user')


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
