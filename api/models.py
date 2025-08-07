from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import uuid
import re


def validate_phone_number(value):
    """
    Validate phone number to be exactly 11 digits for Egyptian numbers
    """
    if not value:
        return value

    # Remove any non-digit characters
    digits_only = re.sub(r"\D", "", value)

    # Handle international format (+20...)
    if digits_only.startswith("20") and len(digits_only) == 12:
        # Convert international to local format
        digits_only = "0" + digits_only[2:]

    # Check if it's exactly 11 digits
    if len(digits_only) != 11:
        raise ValidationError("Phone number must be exactly 11 digits.")

    # Check if it starts with valid Egyptian mobile prefixes
    valid_prefixes = [
        "010",
        "011",
        "012",
        "015",  # Mobile prefixes
        "02",  # Cairo landline
        "03",  # Alexandria landline
        "040",
        "041",
        "042",
        "043",
        "044",
        "045",
        "046",
        "047",
        "048",
        "049",  # Delta region
        "050",
        "051",
        "052",
        "053",
        "054",
        "055",
        "056",
        "057",
        "058",
        "059",  # Upper Egypt
        "060",
        "061",
        "062",
        "063",
        "064",
        "065",
        "066",
        "067",
        "068",
        "069",  # Canal region
        "070",
        "071",
        "072",
        "073",
        "074",
        "075",
        "076",
        "077",
        "078",
        "079",  # Sinai
        "080",
        "081",
        "082",
        "083",
        "084",
        "085",
        "086",
        "087",
        "088",
        "089",  # Red Sea
        "090",
        "091",
        "092",
        "093",
        "094",
        "095",
        "096",
        "097",
        "098",
        "099",  # New Valley
    ]

    if not any(digits_only.startswith(prefix) for prefix in valid_prefixes):
        raise ValidationError(
            "Phone number must start with a valid Egyptian mobile or landline prefix."
        )

    return digits_only


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ("patient", "Patient"),
        ("doctor", "Doctor"),
        ("admin", "Admin"),
    )

    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default="patient"
    )
    phone = models.CharField(
        max_length=15, blank=True, null=True, validators=[validate_phone_number]
    )
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=True, null=True
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"

    def __str__(self):
        return f"{self.username} - {self.user_type}"


class Clinic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=11, validators=[validate_phone_number])
    email = models.EmailField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "clinics"

    def __str__(self):
        return self.name


class Doctor(models.Model):
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="doctor_profile"
    )
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    license_number = models.CharField(max_length=50, unique=True)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name="doctors")
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    bio = models.TextField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "doctors"

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="patient_profile"
    )
    medical_history = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(
        max_length=15, blank=True, null=True, validators=[validate_phone_number]
    )
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    blood_type = models.CharField(max_length=5, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "patients"

    def __str__(self):
        return f"{self.user.get_full_name()} - Patient"


class DoctorSchedule(models.Model):
    DAY_CHOICES = (
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    )

    SCHEDULE_TYPE_CHOICES = (
        ("recurring", "Recurring Weekly"),
        ("specific", "Specific Date"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="schedules"
    )
    schedule_type = models.CharField(
        max_length=10, choices=SCHEDULE_TYPE_CHOICES, default="recurring"
    )
    # For recurring schedules
    day = models.CharField(max_length=10, choices=DAY_CHOICES, blank=True, null=True)
    # For specific date schedules
    specific_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True, help_text="Optional notes (e.g., 'Holiday', 'Conference')")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "doctor_schedules"
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'day'],
                condition=models.Q(schedule_type='recurring'),
                name='unique_doctor_recurring_day'
            ),
            models.UniqueConstraint(
                fields=['doctor', 'specific_date'],
                condition=models.Q(schedule_type='specific'),
                name='unique_doctor_specific_date'
            ),
        ]

    def clean(self):
        super().clean()
        if self.schedule_type == "recurring" and not self.day:
            raise ValidationError("Day is required for recurring schedules.")
        if self.schedule_type == "specific" and not self.specific_date:
            raise ValidationError("Specific date is required for specific date schedules.")
        if self.schedule_type == "recurring" and self.specific_date:
            raise ValidationError("Specific date should not be set for recurring schedules.")
        if self.schedule_type == "specific" and self.day:
            raise ValidationError("Day should not be set for specific date schedules.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.schedule_type == "recurring":
            return f"{self.doctor.user.get_full_name()} - {self.day} ({self.start_time}-{self.end_time})"
        else:
            return f"{self.doctor.user.get_full_name()} - {self.specific_date} ({self.start_time}-{self.end_time})"


class Appointment(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
        ("no_show", "No Show"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="appointments"
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="appointments"
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "appointments"
        ordering = ["-appointment_date", "-appointment_time"]

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {self.doctor.user.get_full_name()} - {self.appointment_date}"
