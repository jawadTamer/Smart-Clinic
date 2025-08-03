from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Doctor, Patient, Clinic, DoctorSchedule, Appointment


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


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["user", "blood_type", "emergency_contact", "created_at"]
    list_filter = ["blood_type", "created_at"]
    search_fields = ["user__username", "user__first_name", "user__last_name"]
    ordering = ["user__first_name"]


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
