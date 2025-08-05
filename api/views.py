from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime, timedelta
from django.http import FileResponse, Http404
from django.conf import settings
import os


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


@api_view(["GET"])
@permission_classes([AllowAny])
def serve_media_file(request, file_path):
    try:
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        if not os.path.abspath(full_path).startswith(
            os.path.abspath(settings.MEDIA_ROOT)
        ):
            raise Http404("File not found")
        if not os.path.exists(full_path):
            raise Http404("File not found")
        response = FileResponse(open(full_path, "rb"))
        file_extension = os.path.splitext(file_path)[1].lower()
        content_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".pdf": "application/pdf",
        }
        content_type = content_types.get(file_extension, "application/octet-stream")
        response["Content-Type"] = content_type
        return response
    except (OSError, IOError):
        raise Http404("File not found")


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    data = request.data.copy()
    if "profile_picture" in request.FILES:
        profile_picture = request.FILES["profile_picture"]
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif"]
        if profile_picture.content_type not in allowed_types:
            return Response(
                {
                    "error": "Invalid file type. Only JPEG, PNG, and GIF images are allowed."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if profile_picture.size > 5 * 1024 * 1024:
            return Response(
                {"error": "File size too large. Maximum size is 5MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data["profile_picture"] = profile_picture
    serializer = RegisterSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        if user.user_type == "patient":
            medical_history = request.data.get("medical_history", "")
            allergies = request.data.get("allergies", "")
            emergency_contact = request.data.get("emergency_contact", "")
            emergency_contact_name = request.data.get("emergency_contact_name", "")
            blood_type = request.data.get("blood_type", "")
            patient_data = {
                "medical_history": medical_history if medical_history.strip() else None,
                "allergies": allergies if allergies.strip() else None,
                "emergency_contact": (
                    emergency_contact if emergency_contact.strip() else None
                ),
                "emergency_contact_name": (
                    emergency_contact_name if emergency_contact_name.strip() else None
                ),
                "blood_type": blood_type if blood_type.strip() else None,
            }
            Patient.objects.create(user=user, **patient_data)
        elif user.user_type == "doctor":
            clinic_data = request.data.get("new_clinic")
            clinic_id = request.data.get("clinic")
            from myproject.api.models import Doctor

            license_number = request.data.get("license_number")

            if Doctor.objects.filter(license_number=license_number).exists():
                user.delete()
                return Response(
                    {"error": "A doctor with this license number already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if clinic_data:
                clinic_serializer = ClinicSerializer(data=clinic_data)
                if clinic_serializer.is_valid():
                    clinic = clinic_serializer.save()
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
                    user.delete()
                    return Response(
                        clinic_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            elif clinic_id:
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
                user.delete()
                return Response(
                    {"error": "Clinic information is required for doctor registration"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
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
    user = request.user
    serializer = UserSerializer(user)
    data = serializer.data
    # Add doctor_id or patient_id if available
    doctor_id = None
    patient_id = None
    if user.user_type == "doctor":
        try:
            doctor_id = user.doctor_profile.id
        except Exception:
            doctor_id = None
    if user.user_type == "patient":
        try:
            patient_id = user.patient_profile.id
        except Exception:
            patient_id = None
    data["doctor_id"] = doctor_id
    data["patient_id"] = patient_id
    return Response(data)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user = request.user
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Profile updated successfully", "user": serializer.data},
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorListView(generics.ListAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Doctor.objects.filter(is_available=True)
        specialization = self.request.query_params.get("specialization", None)
        if specialization:
            queryset = queryset.filter(specialization=specialization)
        return queryset


class DoctorDetailView(generics.RetrieveAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"


class DoctorScheduleUpdateView(generics.UpdateAPIView):
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsDoctor, IsOwnerOrAdmin]

    def get_queryset(self):
        return DoctorSchedule.objects.filter(doctor__user=self.request.user)

    def get_object(self):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        schedule_id = self.kwargs.get("schedule_id")
        return get_object_or_404(DoctorSchedule, id=schedule_id, doctor=doctor)


class PatientProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsPatientOrDoctorOrAdmin, IsPatientOwnerOrDoctorOrAdmin]

    def get_object(self):
        if self.request.user.user_type == "patient":
            return get_object_or_404(Patient, user=self.request.user)
        if self.request.user.user_type in ["doctor", "admin"]:
            patient_id = self.request.query_params.get("patient_id")
            if patient_id:
                return get_object_or_404(Patient, id=patient_id)
            else:
                return Patient.objects.first()
        return get_object_or_404(Patient, user=self.request.user)


class PatientDetailView(generics.RetrieveAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsDoctorOrAdmin]
    queryset = Patient.objects.all()
    lookup_field = "id"


class AppointmentCreateView(generics.CreateAPIView):
    serializer_class = AppointmentCreateSerializer
    permission_classes = [IsPatient]

    def perform_create(self, serializer):
        patient = get_object_or_404(Patient, user=self.request.user)
        serializer.save(patient=patient)


class AppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == "admin":
            return Appointment.objects.all()
        elif user.user_type == "doctor":
            doctor = get_object_or_404(Doctor, user=user)
            return Appointment.objects.filter(doctor=doctor)
        elif user.user_type == "patient":
            patient = get_object_or_404(Patient, user=user)
            return Appointment.objects.filter(patient=patient)
        return Appointment.objects.none()


class AppointmentDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AppointmentUpdateSerializer
    permission_classes = [IsAppointmentOwnerOrDoctor]
    queryset = Appointment.objects.all()
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AppointmentSerializer
        return AppointmentUpdateSerializer


class AdminUserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all()


class AdminClinicViewSet(viewsets.ModelViewSet):
    serializer_class = ClinicSerializer
    permission_classes = [IsAdmin]
    queryset = Clinic.objects.all()


@api_view(["POST"])
@permission_classes([AllowAny])
def create_clinic_public(request):
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
    clinics = Clinic.objects.filter(is_active=True)
    serializer = ClinicSerializer(clinics, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_profile_image(request):
    if "profile_picture" not in request.FILES:
        return Response(
            {"error": "No profile picture file provided"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    profile_picture = request.FILES["profile_picture"]
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif"]
    if profile_picture.content_type not in allowed_types:
        return Response(
            {"error": "Invalid file type. Only JPEG, PNG, and GIF images are allowed."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if profile_picture.size > 5 * 1024 * 1024:
        return Response(
            {"error": "File size too large. Maximum size is 5MB."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        user = request.user
        user.profile_picture = profile_picture
        user.save()
        return Response(
            {
                "message": "Profile image uploaded successfully",
                "profile_picture_url": (
                    user.profile_picture.url if user.profile_picture else None
                ),
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to upload profile image: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class AvailableDoctorsView(generics.ListAPIView):
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
    serializer_class = DoctorScheduleSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        doctor_id = self.kwargs.get("doctor_id")
        if doctor_id:
            return DoctorSchedule.objects.filter(doctor_id=doctor_id)
        return DoctorSchedule.objects.none()


class DoctorScheduleCreateView(generics.CreateAPIView):
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsDoctor]

    def perform_create(self, serializer):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        serializer.save(doctor=doctor)
