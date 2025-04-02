# Farm Surveillance API

A Django REST API for farm surveillance, developed as part of PRT583 PROCESS DEVELOPMENT METHODOLOGIES.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Setup Instructions](#setup-instructions)
  - [Using Docker (Recommended)](#using-docker-recommended)
  - [Manual Setup](#manual-setup)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Environment Variables](#environment-variables)

## Overview

This project is a RESTful API built with Django and Django REST Framework that provides endpoints for farm surveillance functionality.

## Features

- User authentication with JWT
- API documentation with Swagger and ReDoc
- PostgreSQL database integration
- Containerized with Docker

## Requirements

- Python 3.11+
- PostgreSQL 15+
- Docker and Docker Compose (for containerized setup)

## Setup Instructions

### Using Docker (Recommended)

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Configure environment variables (optional)**

   The default configuration should work out of the box with Docker. However, you can modify the environment variables in the `docker-compose.yml` file if needed.

3. **Build and start the containers**

   ```bash
   docker-compose up -d
   ```

4. **Run migrations**

   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Create a superuser (optional)**

   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Access the API**

   The API will be available at http://localhost:8001/

### Manual Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a virtual environment and activate it**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL**

   Install PostgreSQL and create a database:

   ```bash
   createdb backend
   ```

5. **Configure environment variables**

   Create a `.env` file in the project root with the following variables:

   ```
   DEBUG=1
   DJANGO_SETTINGS_MODULE=backend.settings
   DATABASE_URL=postgres://postgres:postgres@localhost:5432/backend
   ```

6. **Run migrations**

   ```bash
   python manage.py migrate
   ```

7. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**

   ```bash
   python manage.py runserver
   ```

9. **Access the API**

   The API will be available at http://localhost:8000/

## API Documentation

The API documentation is available at the following endpoints:

- **Swagger UI**: [/api/v1/schema/swagger-ui/](http://localhost:8001/api/v1/schema/swagger-ui/)
- **ReDoc**: [/api/v1/schema/redoc/](http://localhost:8001/api/v1/schema/redoc/)

## Authentication

The API uses JWT (JSON Web Token) authentication. To authenticate:

1. Obtain a token by sending a POST request to `/api/v1/jwt/create/` with your credentials:

   ```json
   {
     "email": "your-email@example.com",
     "password": "your-password"
   }
   ```

2. Include the token in the Authorization header of your requests:

   ```
   Authorization: JWT <your-token>
   ```

3. To refresh the token, send a POST request to `/api/v1/jwt/refresh/` with your refresh token:

   ```json
   {
     "refresh": "your-refresh-token"
   }
   ```

## Environment Variables

The following environment variables can be configured:

| Variable               | Description               | Default                                      |
| ---------------------- | ------------------------- | -------------------------------------------- |
| DEBUG                  | Debug mode                | 1 (True)                                     |
| DJANGO_SETTINGS_MODULE | Django settings module    | backend.settings                             |
| DATABASE_URL           | PostgreSQL connection URL | postgres://postgres:postgres@db:5432/backend |
| EMAIL_HOST_USER        | SMTP email username       | your_email@gmail.com                         |
| EMAIL_HOST_PASSWORD    | SMTP email password       | your_email_password                          |

For production deployment, make sure to:

- Set `DEBUG=0`
- Change the `SECRET_KEY` in settings.py
- Configure proper `ALLOWED_HOSTS`
- Set up proper email credentials
