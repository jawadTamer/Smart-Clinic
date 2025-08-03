from rest_framework import permissions


class IsPatient(permissions.BasePermission):
    """
    Allow access only to patients.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "patient"


class IsDoctor(permissions.BasePermission):
    """
    Allow access only to doctors.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "doctor"


class IsAdmin(permissions.BasePermission):
    """
    Allow access only to admins.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == "admin"


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allow access to object owner or admin.
    """

    def has_object_permission(self, request, view, obj):

        if request.user.user_type == "admin":
            return True

        if hasattr(obj, "user"):
            return obj.user == request.user
        elif hasattr(obj, "patient"):
            return obj.patient.user == request.user
        elif hasattr(obj, "doctor"):
            return obj.doctor.user == request.user

        return False


class IsAppointmentOwnerOrDoctor(permissions.BasePermission):
    """
    Allow access to appointment owner (patient) or the doctor.
    """

    def has_object_permission(self, request, view, obj):
        #
        if request.user.user_type == "admin":
            return True

        if request.user.user_type == "doctor":
            return obj.doctor.user == request.user

        if request.user.user_type == "patient":
            return obj.patient.user == request.user

        return False


class IsDoctorOrAdmin(permissions.BasePermission):
    """
    Allow access to doctors or admins.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in [
            "doctor",
            "admin",
        ]


class IsPatientOrAdmin(permissions.BasePermission):
    """
    Allow access to patients or admins.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in [
            "patient",
            "admin",
        ]


class IsPatientOrDoctorOrAdmin(permissions.BasePermission):
    """
    Allow access to patients, doctors, or admins.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in [
            "patient",
            "doctor",
            "admin",
        ]


class IsPatientOwnerOrDoctorOrAdmin(permissions.BasePermission):
    """
    Allow access to patient owner, doctors, or admins.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.user_type == "admin":
            return True

        if request.user.user_type == "doctor":
            return True  # Doctors can access any patient profile

        if request.user.user_type == "patient":
            return obj.user == request.user

        return False
