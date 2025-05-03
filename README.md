# FastPool Backend

A Django-based backend service for the FastPool application.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Authentication](#authentication)
3. [User Routes](#user-routes)
4. [Driver Routes](#driver-routes)
5. [Rider Routes](#rider-routes)
6. [Ride Routes](#ride-routes)
7. [Setup](#setup)
8. [Contributing](#contributing)
9. [License](#license)

---

## Introduction

FastPool is a ride-sharing backend service built using Django. It provides APIs for user management, ride creation, ride requests, and more. This documentation explains all the available routes, their usage, and examples to help developers integrate with the backend.

---

## Authentication

### `auth_required` Decorator

The `auth_required` decorator is used to secure routes by requiring a valid Supabase authentication token. Here's how it works:

1. **Authorization Header**: Every request to a route protected by `auth_required` must include an `Authorization` header with a Bearer token.

   - Example: `Authorization: Bearer <your_token>`

2. **Token Verification**: The token is verified with Supabase to ensure it is valid and not expired.

3. **User Identification**: If the token is valid, the corresponding user is fetched from the database, and their ID is attached to the request object as `request.user_id`.

4. **Error Handling**:
   - If the token is missing or invalid, an `AuthenticationFailed` error is returned with a `401 Unauthorized` status.
   - If the user is not found in the database, a `404 Not Found` error is returned.

---

## User Routes

### 1. **Signup**

- **URL**: `/users/signup/`
- **Method**: `POST`
- **Description**: Registers a new user and sends a verification email with an OTP.
- **Headers**: None
- **Body Parameters**:
  - `username` (string, required): The username of the user.
  - `email` (string, required): The email address of the user.
  - `password` (string, required): The password for the user.
- **Example**:
  ```bash
  curl -X POST http://127.0.0.1:8000/users/signup/ \
    -H "Content-Type: application/json" \
    -d '{"username": "john_doe", "email": "john@example.com", "password": "securepassword"}'
  ```

---

### 2. **Login**

- **URL**: `/users/login/`
- **Method**: `POST`
- **Description**: Logs in a user and returns access and refresh tokens.
- **Headers**: None
- **Body Parameters**:
  - `email` (string, required): The email address of the user.
  - `password` (string, required): The password for the user.
- **Example**:
  ```bash
  curl -X POST http://127.0.0.1:8000/users/login/ \
    -H "Content-Type: application/json" \
    -d '{"email": "john@example.com", "password": "securepassword"}'
  ```

---

### 3. **Verify OTP**

- **URL**: `/users/verify/`
- **Method**: `POST`
- **Description**: Verifies the OTP sent to the user's email and completes the registration process.
- **Headers**: None
- **Body Parameters**:
  - `email` (string, required): The email address of the user.
  - `otp` (string, required): The OTP sent to the user's email.
- **Example**:
  ```bash
  curl -X POST http://127.0.0.1:8000/users/verify/ \
    -H "Content-Type: application/json" \
    -d '{"email": "john@example.com", "otp": "123456"}'
  ```

---

### 4. **Resend OTP**

- **URL**: `/users/resend-otp/`
- **Method**: `POST`
- **Description**: Resends the OTP to the user's email.
- **Headers**: None
- **Body Parameters**:
  - `email` (string, required): The email address of the user.
- **Example**:
  ```bash
  curl -X POST http://127.0.0.1:8000/users/resend-otp/ \
    -H "Content-Type: application/json" \
    -d '{"email": "john@example.com"}'
  ```

---

### 5. **Request Password Reset Link**

- **URL**: `/users/request-link/`
- **Method**: `POST`
- **Description**: Sends a password reset link to the user's email.
- **Headers**: None
- **Body Parameters**:
  - `email` (string, required): The email address of the user.
  - `url` (string, required): The base URL for the reset link.
- **Example**:
  ```bash
  curl -X POST http://127.0.0.1:8000/users/request-link/ \
    -H "Content-Type: application/json" \
    -d '{"email": "john@example.com", "url": "http://127.0.0.1:8000/reset-password"}'
  ```

---

### 6. **Reset Password**

- **URL**: `/users/reset/`
- **Method**: `POST`
- **Description**: Resets the user's password using a token.
- **Headers**: None
- **Body Parameters**:
  - `token` (string, required): The reset token.
  - `password` (string, required): The new password.
- **Example**:
  ```bash
  curl -X POST http://127.0.0.1:8000/users/reset/ \
    -H "Content-Type: application/json" \
    -d '{"token": "abc123", "password": "newpassword"}'
  ```

---

### 7. **Edit Profile**

- **URL**: `/users/profile/edit/`
- **Method**: `PUT`
- **Description**: Updates the user's profile information.
- **Headers**:
  - `Authorization` (string, required): Bearer token for authentication.
- **Body Parameters**:
  - `username` (string, optional): The new username.
  - `phone` (string, optional): The new phone number.
  - `gender` (string, optional): The new gender.
- **Example**:
  ```bash
  curl -X PUT http://127.0.0.1:8000/users/profile/edit/ \
    -H "Authorization: Bearer <your_token>" \
    -H "Content-Type: application/json" \
    -d '{"username": "new_username", "phone": "1234567890", "gender": "Female"}'
  ```

---

### 8. **Edit Profile Picture**

- **URL**: `/users/profile/edit-profile-picture/`
- **Method**: `PUT`
- **Description**: Updates the user's profile picture.
- **Headers**:
  - `Authorization` (string, required): Bearer token for authentication.
- **Body Parameters**:
  - `profile_picture` (file, required): The new profile picture file.
- **Example**:
  ```bash
  curl -X PUT http://127.0.0.1:8000/users/profile/edit-profile-picture/ \
    -H "Authorization: Bearer <your_token>" \
    -F "profile_picture=@/path/to/your/image.jpg"
  ```

---

## Driver Routes

### 1. **Register Vehicle**

- **URL**: `/drivers/register-vehicle/`
- **Method**: `POST`
- **Description**: Registers a new vehicle for the driver.
- **Headers**:
  - `Authorization` (string, required): Bearer token for authentication.
- **Body Parameters**:
  - `name` (string, required): The name of the vehicle.
  - `registration_number` (string, required): The registration number of the vehicle.
  - `type` (string, required): The type of the vehicle.
  - `capacity` (integer, required): The seating capacity of the vehicle.
  - `AC` (boolean, required): Whether the vehicle has AC.
- **Example**:
  ```bash
  curl -X POST http://127.0.0.1:8000/drivers/register-vehicle/ \
    -H "Authorization: Bearer <your_token>" \
    -H "Content-Type: application/json" \
    -d '{"name": "Toyota Prius", "registration_number": "ABC123", "type": "Sedan", "capacity": 4, "AC": true}'
  ```

---

## Rider Routes

### 1. **Ride History**

- **URL**: `/riders/history/`
- **Method**: `GET`
- **Description**: Fetches the ride history of the rider.
- **Headers**:
  - `Authorization` (string, required): Bearer token for authentication.
- **Example**:
  ```bash
  curl -X GET http://127.0.0.1:8000/riders/history/ \
    -H "Authorization: Bearer <your_token>"
  ```

---

## Ride Routes

### 1. **Create Ride**

- **URL**: `/rides/`
- **Method**: `POST`
- **Description**: Creates a new ride.
- **Headers**:
  - `Authorization` (string, required): Bearer token for authentication.
- **Body Parameters**:
  - `source_lat` (float, required): Latitude of the source location.
  - `source_lng` (float, required): Longitude of the source location.
  - `destination_lat` (float, required): Latitude of the destination location.
  - `destination_lng` (float, required): Longitude of the destination location.
  - `vehicle` (integer, required): ID of the vehicle to be used.
  - `time` (string, required): Time of the ride.
  - `capacity` (integer, required): Total capacity of the ride.
  - `amount` (integer, required): Fare amount for the ride.
  - `date` (string, required): Date of the ride.
- **Example**:
  ```bash
  curl -X POST http://127.0.0.1:8000/rides/ \
    -H "Authorization: Bearer <your_token>" \
    -H "Content-Type: application/json" \
    -d '{"source_lat": 37.7749, "source_lng": -122.4194, "destination_lat": 34.0522, "destination_lng": -118.2437, "vehicle": 1, "time": "10:00:00", "capacity": 4, "amount": 100, "date": "2023-10-01"}'
  ```

---

### 2. **Update Ride**

- **URL**: `/rides/edit-ride/`
- **Method**: `PUT`
- **Description**: Updates an existing ride. Only the driver who created the ride can update it.
- **Headers**:
  - `Authorization` (string, required): Bearer token for authentication.
- **Query Parameters**:
  - `id` (integer, required): The ID of the ride to update.
- **Body Parameters**:
  - Any ride field that needs to be updated (e.g., `time`, `capacity`, `amount`).
- **Example**:
  ```bash
  curl -X PUT http://127.0.0.1:8000/rides/edit-ride/?id=1 \
    -H "Authorization: Bearer <your_token>" \
    -H "Content-Type: application/json" \
    -d '{"time": "12:00:00", "capacity": 3, "amount": 150}'
  ```

---

### 3. **Delete Ride**

- **URL**: `/rides/<ride_id>/`
- **Method**: `DELETE`
- **Description**: Deletes a ride. Only the driver who created the ride can delete it.
- **Headers**:
  - `Authorization` (string, required): Bearer token for authentication.
- **Example**:
  ```bash
  curl -X DELETE http://127.0.0.1:8000/rides/1/ \
    -H "Authorization: Bearer <your_token>"
  ```

---

### 4. **List Rides**

- **URL**: `/rides/`
- **Method**: `GET`
- **Description**: Fetches a list of rides based on the user's role (driver or rider).
- **Headers**:
  - `Authorization` (string, required): Bearer token for authentication.
- **Query Parameters**:
  - `role` (string, required): The role of the user (`driver` or `rider`).
- **Example**:
  ```bash
  curl -X GET http://127.0.0.1:8000/rides/?role=driver \
    -H "Authorization: Bearer <your_token>"
  ```

---

### 5. **Accept Ride Request**

- **URL**: `/ride/requests/accept/`
- **Method**: `POST`
- **Description**: Accepts a ride request. Only the driver of the ride can accept requests.
- **Headers**:
  - `Authorization` (string, required): Bearer token for authentication.
- **Body Parameters**:
  - `id` (integer, required): The ID of the ride request to accept.
- **Example**:
  ```bash
  curl -X POST http://127.0.0.1:8000/ride/requests/accept/ \
    -H "Authorization: Bearer <your_token>" \
    -H "Content-Type: application/json" \
    -d '{"id": 5}'
  ```

---

## Setup

<span style="color: red; font-weight: bold;">Note:</span> <span style="font-weight: bold;">Please follow the instructions carefully.</span>

1. Clone the repository

```bash
git clone <repository-url> fastpool-be
cd fastpool-be
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure environment variables
   Create a `.env` file in the root directory with the following variables:

```
NAME=your_db_name
USER=your_db_user
PASSWORD=your_db_password
HOST=your_db_host
PORT=your_db_port
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

4. Run migrations

```bash
python manage.py migrate
```

5. Start the development server

```bash
python manage.py runserver
```

---

## Contributing

[To be added]

---

## License

[To be added]
