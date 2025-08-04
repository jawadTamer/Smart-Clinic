from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User, Doctor, Patient, Clinic, DoctorSchedule, Appointment


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with all user fields"""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "user_type",
            "phone",
            "address",
            "date_of_birth",
            "gender",
            "profile_picture",
            "is_active",
        )


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = [
        "username",
        "email",
        "first_name",
        "last_name",
        "user_type",
        "is_active",
        "created_at",
    ]
    list_filter = ["user_type", "is_active", "gender", "created_at"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["-created_at"]

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "user_type",
                    "phone",
                    "address",
                    "date_of_birth",
                    "gender",
                    "profile_picture",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "user_type",
                    "phone",
                    "address",
                    "date_of_birth",
                    "gender",
                    "profile_picture",
                )
            },
        ),
    )


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "email", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "address", "phone", "email"]
    ordering = ["name"]


class DoctorCreationForm(CustomUserCreationForm):
    """Form for creating doctors with all user fields and doctor-specific fields"""

    specialization = forms.ChoiceField(choices=Doctor.SPECIALIZATION_CHOICES)
    license_number = forms.CharField(max_length=50)
    clinic = forms.ModelChoiceField(queryset=Clinic.objects.all())
    experience_years = forms.IntegerField(min_value=0, initial=0)
    consultation_fee = forms.DecimalField(max_digits=10, decimal_places=2, initial=0.00)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    is_available = forms.BooleanField(initial=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set user_type to doctor by default
        self.fields["user_type"].initial = "doctor"


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "specialization",
        "license_number",
        "clinic",
        "experience_years",
        "is_available",
    ]
    list_filter = ["specialization", "is_available", "clinic", "created_at"]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "license_number",
    ]
    ordering = ["user__first_name"]

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:  # Adding new doctor
            return DoctorCreationForm
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:  # Creating new doctor
            # Create user first
            user_data = {
                "username": form.cleaned_data["username"],
                "email": form.cleaned_data["email"],
                "first_name": form.cleaned_data["first_name"],
                "last_name": form.cleaned_data["last_name"],
                "user_type": form.cleaned_data["user_type"],
                "phone": form.cleaned_data["phone"],
                "address": form.cleaned_data["address"],
                "date_of_birth": form.cleaned_data["date_of_birth"],
                "gender": form.cleaned_data["gender"],
                "profile_picture": form.cleaned_data.get("profile_picture"),
                "is_active": form.cleaned_data.get("is_active", True),
            }
            user = User.objects.create_user(**user_data)
            user.set_password(form.cleaned_data["password1"])
            user.save()

            # Create doctor profile
            obj.user = user
            obj.specialization = form.cleaned_data["specialization"]
            obj.license_number = form.cleaned_data["license_number"]
            obj.clinic = form.cleaned_data["clinic"]
            obj.experience_years = form.cleaned_data["experience_years"]
            obj.consultation_fee = form.cleaned_data["consultation_fee"]
            obj.bio = form.cleaned_data["bio"]
            obj.is_available = form.cleaned_data["is_available"]

        super().save_model(request, obj, form, change)


class PatientCreationForm(CustomUserCreationForm):
    """Form for creating patients with all user fields and patient-specific fields"""

    medical_history = forms.CharField(widget=forms.Textarea, required=False)
    allergies = forms.CharField(widget=forms.Textarea, required=False)
    emergency_contact = forms.CharField(max_length=15, required=False)
    emergency_contact_name = forms.CharField(max_length=100, required=False)
    blood_type = forms.CharField(max_length=5, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set user_type to patient by default
        self.fields["user_type"].initial = "patient"


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["user", "blood_type", "emergency_contact", "created_at"]
    list_filter = ["blood_type", "created_at"]
    search_fields = ["user__username", "user__first_name", "user__last_name"]
    ordering = ["user__first_name"]

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:  # Adding new patient
            return PatientCreationForm
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:  # Creating new patient
            # Create user first
            user_data = {
                "username": form.cleaned_data["username"],
                "email": form.cleaned_data["email"],
                "first_name": form.cleaned_data["first_name"],
                "last_name": form.cleaned_data["last_name"],
                "user_type": form.cleaned_data["user_type"],
                "phone": form.cleaned_data["phone"],
                "address": form.cleaned_data["address"],
                "date_of_birth": form.cleaned_data["date_of_birth"],
                "gender": form.cleaned_data["gender"],
                "profile_picture": form.cleaned_data.get("profile_picture"),
                "is_active": form.cleaned_data.get("is_active", True),
            }
            user = User.objects.create_user(**user_data)
            user.set_password(form.cleaned_data["password1"])
            user.save()

            # Create patient profile
            obj.user = user
            obj.medical_history = form.cleaned_data["medical_history"]
            obj.allergies = form.cleaned_data["allergies"]
            obj.emergency_contact = form.cleaned_data["emergency_contact"]
            obj.emergency_contact_name = form.cleaned_data["emergency_contact_name"]
            obj.blood_type = form.cleaned_data["blood_type"]

        super().save_model(request, obj, form, change)


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ["doctor", "day", "start_time", "end_time", "is_available"]
    list_filter = ["day", "is_available", "doctor__specialization"]
    search_fields = ["doctor__user__first_name", "doctor__user__last_name"]
    ordering = ["doctor__user__first_name", "day"]


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        "patient",
        "doctor",
        "appointment_date",
        "appointment_time",
        "status",
        "created_at",
    ]
    list_filter = ["status", "appointment_date", "doctor__specialization", "created_at"]
    search_fields = [
        "patient__user__first_name",
        "patient__user__last_name",
        "doctor__user__first_name",
        "doctor__user__last_name",
    ]
    ordering = ["-appointment_date", "-appointment_time"]
    date_hierarchy = "appointment_date"
