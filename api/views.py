from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime, timedelta

from .models import User, Doctor, Patient, Clinic, DoctorSchedule, Appointment
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    ClinicSerializer,
    DoctorSerializer,
    DoctorDetailSerializer,
    PatientSerializer,
    AppointmentSerializer,
    AppointmentCreateSerializer,
    AppointmentUpdateSerializer,
    DoctorScheduleSerializer,
)
from .permissions import (
    IsPatient,
    IsDoctor,
    IsAdmin,
    IsOwnerOrAdmin,
    IsAppointmentOwnerOrDoctor,
    IsDoctorOrAdmin,
    IsPatientOrAdmin,
    IsPatientOrDoctorOrAdmin,
    IsPatientOwnerOrDoctorOrAdmin,
)


# Authentication Views
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Register a new user (patient/doctor)"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Create patient or doctor profile based on user type
        if user.user_type == "patient":
            Patient.objects.create(user=user)
        elif user.user_type == "doctor":
            # Handle clinic creation or selection for doctors
            clinic_data = request.data.get("new_clinic")
            clinic_id = request.data.get("clinic")

            if clinic_data:
                # Create new clinic first
                clinic_serializer = ClinicSerializer(data=clinic_data)
                if clinic_serializer.is_valid():
                    clinic = clinic_serializer.save()
                    # Create doctor with the new clinic
                    doctor_data = {
                        "specialization": request.data.get("specialization"),
                        "license_number": request.data.get("license_number"),
                        "clinic": clinic,
                        "experience_years": request.data.get("experience_years", 0),
                        "consultation_fee": request.data.get("consultation_fee", 0.00),
                        "bio": request.data.get("bio", ""),
                        "is_available": request.data.get("is_available", True),
                    }
                    Doctor.objects.create(user=user, **doctor_data)
                else:
                    # If clinic creation fails, delete the user and return error
                    user.delete()
                    return Response(
                        clinic_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            elif clinic_id:
                # Use existing clinic
                try:
                    clinic = Clinic.objects.get(id=clinic_id)
                    doctor_data = {
                        "specialization": request.data.get("specialization"),
                        "license_number": request.data.get("license_number"),
                        "clinic": clinic,
                        "experience_years": request.data.get("experience_years", 0),
                        "consultation_fee": request.data.get("consultation_fee", 0.00),
                        "bio": request.data.get("bio", ""),
                        "is_available": request.data.get("is_available", True),
                    }
                    Doctor.objects.create(user=user, **doctor_data)
                except Clinic.DoesNotExist:
                    user.delete()
                    return Response(
                        {"error": "Selected clinic does not exist"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                # No clinic provided, delete user and return error
                user.delete()
                return Response(
                    {"error": "Clinic information is required for doctor registration"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "User registered successfully",
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """Login user and return JWT tokens"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful",
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# Doctor Views
class DoctorListView(generics.ListAPIView):
    """List all doctors with optional specialization filter"""

    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Doctor.objects.filter(is_available=True)
        specialization = self.request.query_params.get("specialization", None)
        if specialization:
            queryset = queryset.filter(specialization=specialization)
        return queryset


class DoctorDetailView(generics.RetrieveAPIView):
    """Get doctor details"""

    queryset = Doctor.objects.all()
    serializer_class = DoctorDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"


class DoctorScheduleUpdateView(generics.UpdateAPIView):
    """Update doctor schedule (doctor only)"""

    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsDoctor, IsOwnerOrAdmin]

    def get_queryset(self):
        return DoctorSchedule.objects.filter(doctor__user=self.request.user)

    def get_object(self):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        schedule_id = self.kwargs.get("schedule_id")
        return get_object_or_404(DoctorSchedule, id=schedule_id, doctor=doctor)


# Patient Views
class PatientProfileView(generics.RetrieveUpdateAPIView):
    """Get and update patient profile"""

    serializer_class = PatientSerializer
    permission_classes = [IsPatientOrDoctorOrAdmin, IsPatientOwnerOrDoctorOrAdmin]

    def get_object(self):
        # If user is patient, return their own profile
        if self.request.user.user_type == "patient":
            return get_object_or_404(Patient, user=self.request.user)

        # If user is doctor or admin, they can access any patient profile
        # For now, we'll return the first patient (you might want to add patient_id parameter)
        if self.request.user.user_type in ["doctor", "admin"]:
            patient_id = self.request.query_params.get("patient_id")
            if patient_id:
                return get_object_or_404(Patient, id=patient_id)
            else:
                # Return first patient for demo purposes
                return Patient.objects.first()

        return get_object_or_404(Patient, user=self.request.user)


class PatientDetailView(generics.RetrieveAPIView):
    """Get specific patient profile (for doctors and admins)"""

    serializer_class = PatientSerializer
    permission_classes = [IsDoctorOrAdmin]
    queryset = Patient.objects.all()
    lookup_field = "id"


# Appointment Views
class AppointmentCreateView(generics.CreateAPIView):
    """Create new appointment (patient only)"""

    serializer_class = AppointmentCreateSerializer
    permission_classes = [IsPatient]

    def perform_create(self, serializer):
        patient = get_object_or_404(Patient, user=self.request.user)
        serializer.save(patient=patient)


class AppointmentListView(generics.ListAPIView):
    """List appointments based on user role"""

    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.user_type == "admin":
            # Admin sees all appointments
            return Appointment.objects.all()
        elif user.user_type == "doctor":
            # Doctor sees their appointments
            doctor = get_object_or_404(Doctor, user=user)
            return Appointment.objects.filter(doctor=doctor)
        elif user.user_type == "patient":
            # Patient sees their appointments
            patient = get_object_or_404(Patient, user=user)
            return Appointment.objects.filter(patient=patient)

        return Appointment.objects.none()


class AppointmentDetailView(generics.RetrieveUpdateAPIView):
    """Get and update appointment details"""

    serializer_class = AppointmentUpdateSerializer
    permission_classes = [IsAppointmentOwnerOrDoctor]
    queryset = Appointment.objects.all()
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AppointmentSerializer
        return AppointmentUpdateSerializer


# Admin Views
class AdminUserListView(generics.ListAPIView):
    """List all users (admin only)"""

    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all()


class AdminClinicViewSet(viewsets.ModelViewSet):
    """Manage clinics (admin only)"""

    serializer_class = ClinicSerializer
    permission_classes = [IsAdmin]
    queryset = Clinic.objects.all()


# Public Clinic Creation
@api_view(["POST"])
@permission_classes([AllowAny])
def create_clinic_public(request):
    """Create a new clinic (public access for doctor registration)"""
    serializer = ClinicSerializer(data=request.data)
    if serializer.is_valid():
        clinic = serializer.save()
        return Response(
            {"message": "Clinic created successfully", "clinic": serializer.data},
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_clinics_public(request):
    """List all active clinics (public access for doctor registration)"""
    clinics = Clinic.objects.filter(is_active=True)
    serializer = ClinicSerializer(clinics, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Additional Views
class AvailableDoctorsView(generics.ListAPIView):
    """Get available doctors for a specific date and time"""

    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        date_str = self.request.query_params.get("date")
        time_str = self.request.query_params.get("time")

        if not date_str or not time_str:
            return Doctor.objects.filter(is_available=True)

        try:
            appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            appointment_time = datetime.strptime(time_str, "%H:%M").time()
            day_name = appointment_date.strftime("%A")

            # Get doctors available on this day and time
            available_doctors = Doctor.objects.filter(
                is_available=True,
                schedules__day=day_name,
                schedules__start_time__lte=appointment_time,
                schedules__end_time__gte=appointment_time,
                schedules__is_available=True,
            ).exclude(
                appointments__appointment_date=appointment_date,
                appointments__appointment_time=appointment_time,
                appointments__status__in=["pending", "confirmed"],
            )

            return available_doctors
        except ValueError:
            return Doctor.objects.filter(is_available=True)


class DoctorScheduleListView(generics.ListAPIView):
    """Get doctor schedules"""

    serializer_class = DoctorScheduleSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        doctor_id = self.kwargs.get("doctor_id")
        if doctor_id:
            return DoctorSchedule.objects.filter(doctor_id=doctor_id)
        return DoctorSchedule.objects.none()
