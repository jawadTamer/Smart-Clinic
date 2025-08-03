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

- **Admin Only**: Add, update, delete clinics
- **Read Access for All**: View clinic information

### 6. Authentication & Security

#### JWT Authentication:

- **Access Token**: For API access (limited validity)
- **Refresh Token**: To renew access tokens
- **Request Protection**: All requests (except registration and login) require authentication

#### Permission Verification:

- **System-level Permissions**: Based on user type
- **Object-level Permissions**: Access to personal data only
- **Special Permissions**: Doctors can access patient profiles

### 7. Data Validation

#### Phone Number Validation:

- **Length**: Must be exactly 11 digits
- **Egyptian Numbers Only**: Supports local and international Egyptian numbers
- **Valid Prefixes**: Validates number prefix correctness

#### Appointment Validation:

- **Availability**: Checks doctor availability at specified time
- **Date**: Ensures appointment date is in the future
- **Duplication**: Prevents double booking at same time

### 8. API Features

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

### 9. Frontend Integration

#### CORS Support:

- **Angular Support**: CORS settings customized for frontend
- **Cross-Origin Requests**: Support for requests from different domains
- **Security**: Production-ready security settings

#### Enhanced Responses:

- **Data Formatting**: Format suitable for frontend
- **Related Data**: Include related data in responses
- **Clear Errors**: Clear and helpful error messages

### 10. Production Settings

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
