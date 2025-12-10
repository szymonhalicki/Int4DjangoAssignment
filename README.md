# Multi-Tenant Task Management API

A Django REST API built with Django Ninja demonstrating multi-tenancy with data isolation between organizations. 

## Features

- **Multi-Tenancy**: Complete data isolation between organizations
- **JWT Authentication**: Token-based authentication with 8-hour expiration
- **Task Management**: Create, read, update, delete tasks within your organization
- **User Management**: Manage users within your organization
- **Automatic OpenAPI Docs**: Built-in Swagger UI and ReDoc documentation at `/api/docs`
- **Comprehensive Tests**: Full test coverage with multi-tenancy isolation tests

## Tech Stack

- **Framework**: Django 5.2.9
- **API**: Django Ninja 1.5.0
- **Authentication**: PyJWT 2.10.1
- **Validation**: Pydantic 2.12.5
- **Database**: SQLite (configurable)
- **Testing**: Django TestCase with coverage

## Local Development Setup

### Prerequisites

- Python 3.9+
- pip and venv

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Int4DjangoAssignment
```

2. **Create and activate virtual environment**
   
#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```
4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create test data**
```bash
python manage.py seed_db
```

6. **Start dev server**
```bash
python manage.py runserver
```

#### API will be available at http://localhost:8000/api/v1/
#### OpenAPI documentation at http://localhost:8000/api/v1/docs

## Running tests

### Run all:
```bash
python manage.py test
```

### Coverage report
```bash
coverage run --source='.' manage.py test

coverage report -m
```


## Multi-tenancy

### Files:
- tenant.py - Simple organization context management
- middleware.py - JWT decoding and organization context setting
- models.py - Custom managers with automatic tenant filtering
- auth.py - Ninja authentication handler
- schemas.py - Models for request/response validation

### Tests:
- test_multi_tenancy - Verifies users from different orgs see only their data
- test_update_task_from_different_org - Confirms tasks from other orgs are inaccessible
- test_delete_task_from_different_org - Ensures tasks from other orgs cannot be deleted
- test_user_list_is_tenant_isolated - Verifies user list only shows current org users