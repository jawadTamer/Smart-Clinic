# Smart Clinic API Documentation

## Overview

The Smart Clinic API is a comprehensive clinic management system built with Django REST Framework and JWT Authentication. The system provides full management for patients, doctors, appointments, and clinics.

## 🚀 Core System Features

### 1. Multi-Role User System

#### User Types:

- **Patient**: Can book appointments, view medical profile, update personal information
- **Doctor**: Can manage schedule, view appointments, access patient profiles
- **Admin**: Full system management permissions

#### User Data:

- **Basic Information**: Username, email, first name, last name
- **Contact Details**: Phone number (Egyptian numbers only - 11 digits)
- **Personal Data**: Date of birth, gender, address
- **User Type**: Patient, doctor, or admin

### 2. Doctor Management

#### Doctor Information:

- **Medical Specialization**: Cardiology, Dermatology, Neurology, Orthopedics, Pediatrics, Psychiatry, General, Dental, Eye, Surgery
- **Professional Data**: License number, years of experience, consultation fee
- **Biography**: Brief description of doctor's expertise
- **Clinic**: Associated clinic information

#### Doctor Schedule:

- **Schedule Management**: Doctors can update working hours for each day
- **Available Times**: Set start and end times for each day
- **Availability Status**: Enable/disable doctor availability

### 3. Patient Management

#### Medical Profile:

- **Medical History**: Previous and current medical conditions
- **Allergies**: Substances the patient is allergic to
- **Blood Type**: Patient's blood type
- **Emergency Contact**: Name and phone number for emergency situations

#### Access Permissions:

- **Self Access**: Patients can only view and update their own profile
- **Doctor Access**: Doctors can access all patient profiles
- **Admin Access**: Admin has full permissions on all profiles

### 4. Appointment System

#### Booking Appointments:

- **Browse Doctors**: View doctors by specialization
- **Select Date & Time**: Choose from doctor's available slots
- **Visit Reason**: Brief description of appointment purpose
- **Appointment Status**: Pending, confirmed, cancelled, completed, no-show

#### Appointment Management:

- **For Patients**: View only their own appointments
- **For Doctors**: View their appointments and update status
- **For Admin**: Manage all appointments in the system

### 5. Clinic Management

#### Clinic Information:

- **Basic Data**: Clinic name, address, phone, email
- **Description**: Brief description of clinic and services
- **Doctors**: List of doctors working at the clinic

#### Permissions:

- **Public Access**: Create new clinics (for doctor registration)
- **Admin Only**: Update, delete clinics
- **Read Access for All**: View clinic information

### 6. Clinic Access Permissions

#### Public Clinic Access:

- **Who Can Access**: Anyone (public, authenticated users, doctors, patients, admins)
- **What They See**: All active clinics only
- **Purpose**: For doctor registration and public clinic browsing

#### Admin Clinic Access:

- **Who Can Access**: Administrators only
- **What They See**: All clinics (both active and inactive)
- **Purpose**: Full clinic management and administration

### 7. Authentication & Security

#### JWT Authentication:

- **Access Token**: For API access (limited validity)
- **Refresh Token**: To renew access tokens
- **Request Protection**: All requests (except registration and login) require authentication

#### Permission Verification:

- **System-level Permissions**: Based on user type
- **Object-level Permissions**: Access to personal data only
- **Special Permissions**: Doctors can access patient profiles

### 8. Data Validation

#### Phone Number Validation:

- **Length**: Must be exactly 11 digits
- **Egyptian Numbers Only**: Supports local and international Egyptian numbers
- **Valid Prefixes**: Validates number prefix correctness

#### Appointment Validation:

- **Availability**: Checks doctor availability at specified time
- **Date**: Ensures appointment date is in the future
- **Duplication**: Prevents double booking at same time

### 9. API Features

#### RESTful API:

- **Standard Methods**: GET, POST, PUT, DELETE
- **Unified Responses**: Consistent JSON format
- **Status Codes**: Standard HTTP status codes

#### Pagination & Filtering:

- **Pagination**: Support for long lists
- **Filtering**: Filter by specialization, date, status
- **Search**: Ability to search through data

#### Comprehensive Documentation:

- **Usage Examples**: cURL examples for each endpoint
- **Detailed Descriptions**: Detailed explanation of each API
- **Status Codes**: Explanation of all response codes

### 10. Frontend Integration

#### CORS Support:

- **Angular Support**: CORS settings customized for frontend
- **Cross-Origin Requests**: Support for requests from different domains
- **Security**: Production-ready security settings

#### Enhanced Responses:

- **Data Formatting**: Format suitable for frontend
- **Related Data**: Include related data in responses
- **Clear Errors**: Clear and helpful error messages

### 11. Production Settings

#### Security:

- **JWT Secrets**: Configurable secret keys
- **CORS**: Security settings for cross-origin requests
- **CSRF**: Protection against CSRF attacks

#### Performance:

- **Database**: PostgreSQL support for production
- **Static Files**: Static and media file management
- **Caching**: Caching settings

#### Deployment:

- **Environment Variables**: Configurable settings
- **Docker**: Docker container support
- **CI/CD**: Continuous integration/deployment support

## Base URL

Development: `http://127.0.0.1:8000/api/`
Production: `https://your-domain.com/api/`

## New Public Clinic Endpoints

### Create Clinic (Public Access)

**POST** `/api/clinics/create/`

Create a new clinic for doctor registration purposes.

**Request Body:**

```json
{
  "name": "Clinic Name",
  "address": "Clinic Address",
  "phone": "01234567890",
  "email": "clinic@example.com",
  "description": "Clinic description (optional)"
}
```

**Response:**

```json
{
  "message": "Clinic created successfully",
  "clinic": {
    "id": "uuid",
    "name": "Clinic Name",
    "address": "Clinic Address",
    "phone": "01234567890",
    "email": "clinic@example.com",
    "description": "Clinic description",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### List Clinics (Public Access)

**GET** `/api/clinics/`

Get all active clinics for selection during doctor registration.

**Response:**

```json
[
  {
    "id": "uuid",
    "name": "Clinic Name",
    "address": "Clinic Address",
    "phone": "01234567890",
    "email": "clinic@example.com",
    "description": "Clinic description",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

## Clinic Access Endpoints

### List All Active Clinics (Public Access)

**GET** `/api/clinics/`

Get all active clinics. This endpoint is accessible to anyone (public access).

**Headers:**

```
Content-Type: application/json
```

**No authentication required** - This is a public endpoint.

**Response (Success - 200 OK):**

```json
[
  {
    "id": "uuid",
    "name": "Clinic Name",
    "address": "Clinic Address",
    "phone": "01234567890",
    "email": "clinic@example.com",
    "description": "Clinic description",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

**cURL Example:**

```bash
curl -X GET \
  https://smart-clinic-api.fly.dev/api/clinics/
```

**Note:** This endpoint returns only active clinics (`is_active: true`). For access to all clinics (including inactive ones), administrators can use the admin interface.

## Updated Doctor Registration

The doctor registration endpoint now supports clinic creation during registration:

**POST** `/api/auth/register/`

**Request Body (with new clinic):**

```json
{
  "username": "doctor_username",
  "email": "doctor@example.com",
  "password": "password123",
  "password2": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "01234567890",
  "user_type": "doctor",
  "specialization": "Cardiology",
  "license_number": "MED123456",
  "experience_years": 10,
  "consultation_fee": 500.0,
  "bio": "Experienced cardiologist",
  "new_clinic": {
    "name": "New Clinic",
    "address": "Clinic Address",
    "phone": "01234567890",
    "email": "clinic@example.com",
    "description": "Clinic description"
  }
}
```

**Request Body (with existing clinic):**

```json
{
  "username": "doctor_username",
  "email": "doctor@example.com",
  "password": "password123",
  "password2": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "01234567890",
  "user_type": "doctor",
  "specialization": "Cardiology",
  "license_number": "MED123456",
  "experience_years": 10,
  "consultation_fee": 500.0,
  "bio": "Experienced cardiologist",
  "clinic": "existing-clinic-uuid"
}
```

## Profile Image Management Endpoints
