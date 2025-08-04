from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
import re
from .models import User, Doctor, Patient, Clinic, DoctorSchedule, Appointment


def validate_phone_number(value):
    """
    Validate phone number to be exactly 11 digits for Egyptian numbers
    """
    # Remove any non-digit characters
    digits_only = re.sub(r"\D", "", value)

    # Handle international format (+20...)
    if digits_only.startswith("20") and len(digits_only) == 12:
        # Convert international to local format
        digits_only = "0" + digits_only[2:]

    # Check if it's exactly 11 digits
    if len(digits_only) != 11:
        raise serializers.ValidationError("Phone number must be exactly 11 digits.")

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
        raise serializers.ValidationError(
            "Phone number must start with a valid Egyptian mobile or landline prefix."
        )

    return digits_only


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
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
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    phone = serializers.CharField(validators=[validate_phone_number])

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "user_type",
            "phone",
            "address",
            "date_of_birth",
            "gender",
            "profile_picture",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials.")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
            attrs["user"] = user
            return attrs
        else:
            raise serializers.ValidationError("Must include username and password.")


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class DoctorScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSchedule
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    clinic = ClinicSerializer(read_only=True)
    schedules = DoctorScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class DoctorDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    clinic = ClinicSerializer(read_only=True)
    schedules = DoctorScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["doctor", "appointment_date", "appointment_time", "reason"]

    def validate(self, attrs):
        # Check if doctor is available
        doctor = attrs["doctor"]
        if not doctor.is_available:
            raise serializers.ValidationError(
                "Doctor is not available for appointments."
            )

        # Check if appointment time is within doctor's schedule
        appointment_date = attrs["appointment_date"]
        appointment_time = attrs["appointment_time"]

        # Get day name from date
        from datetime import datetime

        day_name = appointment_date.strftime("%A")

        try:
            schedule = DoctorSchedule.objects.get(doctor=doctor, day=day_name)
            if not schedule.is_available:
                raise serializers.ValidationError(
                    "Doctor is not available on this day."
                )

            if (
                appointment_time < schedule.start_time
                or appointment_time > schedule.end_time
            ):
                raise serializers.ValidationError(
                    "Appointment time is outside doctor's working hours."
                )
        except DoctorSchedule.DoesNotExist:
            raise serializers.ValidationError("Doctor has no schedule for this day.")

        # Check if appointment time is not already booked
        existing_appointment = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status__in=["pending", "confirmed"],
        ).exists()

        if existing_appointment:
            raise serializers.ValidationError("This time slot is already booked.")

        return attrs


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["status", "notes"]
        read_only_fields = [
            "id",
            "patient",
            "doctor",
            "appointment_date",
            "appointment_time",
            "reason",
            "created_at",
            "updated_at",
        ]
