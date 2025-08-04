from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r"admin/clinics", views.AdminClinicViewSet)

urlpatterns = [
    # Authentication
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.login, name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/me/", views.get_user_profile, name="user_profile"),
    path(
        "users/upload-profile-image/",
        views.upload_profile_image,
        name="upload_profile_image",
    ),
    path(
        "users/update-profile/", views.update_user_profile, name="update_user_profile"
    ),
    # Media files
    path("media/<path:file_path>", views.serve_media_file, name="serve_media_file"),
    # Doctors
    path("doctors/", views.DoctorListView.as_view(), name="doctor_list"),
    path("doctors/<uuid:id>/", views.DoctorDetailView.as_view(), name="doctor_detail"),
    path(
        "doctors/schedule/<uuid:schedule_id>/",
        views.DoctorScheduleUpdateView.as_view(),
        name="doctor_schedule_update",
    ),
    path(
        "doctors/<uuid:doctor_id>/schedules/",
        views.DoctorScheduleListView.as_view(),
        name="doctor_schedules",
    ),
    path(
        "doctors/available/",
        views.AvailableDoctorsView.as_view(),
        name="available_doctors",
    ),
    # Patients
    path("patients/me/", views.PatientProfileView.as_view(), name="patient_profile"),
    path(
        "patients/<uuid:id>/", views.PatientDetailView.as_view(), name="patient_detail"
    ),
    # Appointments
    path("appointments/", views.AppointmentListView.as_view(), name="appointment_list"),
    path(
        "appointments/create/",
        views.AppointmentCreateView.as_view(),
        name="appointment_create",
    ),
    path(
        "appointments/<uuid:id>/",
        views.AppointmentDetailView.as_view(),
        name="appointment_detail",
    ),
    # Admin
    path("admin/users/", views.AdminUserListView.as_view(), name="admin_users"),
    path("clinics/", views.list_clinics_public, name="list_clinics_public"),
    path("clinics/create/", views.create_clinic_public, name="create_clinic_public"),
    path("", include(router.urls)),
]
