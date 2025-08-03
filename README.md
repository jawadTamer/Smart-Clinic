# Smart Clinic - Django REST API

A smart clinic management system built with Django REST Framework and JWT Authentication.

## Key Features

### 👥 Multi-Role User System

- **Patients**: Can book appointments and view their medical profile
- **Doctors**: Can manage their schedule and review appointments
- **Admins**: Full system and clinic management

### 🏥 Clinic Management

- Manage clinics and basic information
- Link doctors to clinics
- Manage schedules

### 📅 Appointment System

- Book appointments with availability checks
- Manage appointment statuses (pending, confirmed, completed, etc.)
- View appointments based on user role

### 🔐 Security

- JWT Authentication
- Role-based permissions
- CORS configured for Angular

## Technologies Used

- **Django 5.2.4**
- **Django REST Framework 3.14.0**
- **JWT Authentication**
- **CORS Headers**
- **PostgreSQL** (Production)
- **SQLite** (Development)

## 🛠️ Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `env.example` to `.env` and configure your local settings
4. Run migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser`
6. Run the server: `python manage.py runserver`

## 📁 Project Structure

```
myproject/
├── api/                    # Main API application
│   ├── models.py          # Database models
│   ├── views.py           # API views
│   ├── serializers.py     # DRF serializers
│   ├── urls.py            # API URLs
│   └── permissions.py     # Custom permissions
├── myproject/             # Django project settings
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔧 Configuration Files

- `env.example`: Example environment variables
- `requirements.txt`: Python dependencies
