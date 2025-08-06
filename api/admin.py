from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db import transaction
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
    
    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if license_number and Doctor.objects.filter(license_number=license_number).exists():
            raise forms.ValidationError("A doctor with this license number already exists.")
        return license_number
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username


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
            try:
                with transaction.atomic():
                    # Create user first
                    user_data = {
                        "username": form.cleaned_data["username"],
                        "email": form.cleaned_data["email"],
                        "first_name": form.cleaned_data["first_name"],
                        "last_name": form.cleaned_data["last_name"],
                        "user_type": "doctor",
                        "phone": form.cleaned_data.get("phone", ""),
                        "address": form.cleaned_data.get("address", ""),
                        "date_of_birth": form.cleaned_data.get("date_of_birth"),
                        "gender": form.cleaned_data.get("gender"),
                        "profile_picture": form.cleaned_data.get("profile_picture"),
                        "is_active": form.cleaned_data.get("is_active", True),
                    }
                    
                    # Check for duplicate license number
                    license_number = form.cleaned_data["license_number"]
                    if Doctor.objects.filter(license_number=license_number).exists():
                        raise forms.ValidationError(f"A doctor with license number {license_number} already exists.")
                    
                    user = User.objects.create_user(**user_data)
                    user.set_password(form.cleaned_data["password1"])
                    user.save()

                    # Create doctor profile
                    obj.user = user
                    obj.specialization = form.cleaned_data["specialization"]
                    obj.license_number = license_number
                    obj.clinic = form.cleaned_data["clinic"]
                    obj.experience_years = form.cleaned_data.get("experience_years", 0)
                    obj.consultation_fee = form.cleaned_data.get("consultation_fee", 0.00)
                    obj.bio = form.cleaned_data.get("bio", "")
                    obj.is_available = form.cleaned_data.get("is_available", True)
                    
                    super().save_model(request, obj, form, change)
                    
            except Exception as e:
                raise forms.ValidationError(f"Failed to create doctor: {str(e)}")
        else:
            super().save_model(request, obj, form, change)


class PatientCreationForm(CustomUserCreationForm):
    """Form for creating patients with all user fields and patient-specific fields"""

    medical_history = forms.CharField(widget=forms.Textarea, required=False)
    allergies = forms.CharField(widget=forms.Textarea, required=False)
    emergency_contact = forms.CharField(max_length=15, required=False)
    emergency_contact_name = forms.CharField(max_length=100, required=False)
    blood_type = forms.CharField(max_length=5, required=False)
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username


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
            try:
                with transaction.atomic():
                    user_data = {
                        "username": form.cleaned_data["username"],
                        "email": form.cleaned_data["email"],
                        "first_name": form.cleaned_data["first_name"],
                        "last_name": form.cleaned_data["last_name"],
                        "user_type": "patient",
                        "phone": form.cleaned_data.get("phone", ""),
                        "address": form.cleaned_data.get("address", ""),
                        "date_of_birth": form.cleaned_data.get("date_of_birth"),
                        "gender": form.cleaned_data.get("gender"),
                        "profile_picture": form.cleaned_data.get("profile_picture"),
                        "is_active": form.cleaned_data.get("is_active", True),
                    }
                    user = User.objects.create_user(**user_data)
                    user.set_password(form.cleaned_data["password1"])
                    user.save()

                    # Create patient profile
                    obj.user = user
                    obj.medical_history = form.cleaned_data.get("medical_history", "")
                    obj.allergies = form.cleaned_data.get("allergies", "")
                    obj.emergency_contact = form.cleaned_data.get("emergency_contact", "")
                    obj.emergency_contact_name = form.cleaned_data.get("emergency_contact_name", "")
                    obj.blood_type = form.cleaned_data.get("blood_type", "")
                    
                    super().save_model(request, obj, form, change)
                    
            except Exception as e:
                raise forms.ValidationError(f"Failed to create patient: {str(e)}")
        else:
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
