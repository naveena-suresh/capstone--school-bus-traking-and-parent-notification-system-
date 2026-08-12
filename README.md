# 🚌 School Bus Tracking System

## 1. Project Overview

The School Bus Tracking System is a web-based application designed to
improve school transportation management and provide parents and
school administrators with important bus and student information.

The system allows users to manage student details, parent information,
bus details, driver information, route information and live bus
location.

---

## 2. Problem Statement

Parents and schools may face difficulties in knowing the current
location and status of school buses.

Traditional communication methods may not provide real-time
information about:

- Bus location
- Bus status
- Student information
- Driver information
- Route information
- Estimated arrival time
- Bus notifications

This project provides a centralized web-based solution for managing
and monitoring school bus transportation.

---

## 3. Objectives

The main objectives of the project are:

1. Store student information securely.
2. Store parent information.
3. Manage school bus details.
4. Store driver and route information.
5. Track the current bus location.
6. Display latitude and longitude.
7. Display bus speed.
8. Provide estimated arrival information.
9. Display bus notifications.
10. Show overall system status.
11. Display total number of buses and students.

---

## 4. Main Features

### Student Management

- Add student name
- Add student ID
- Add parent name
- Add phone number
- Add bus stop
- Save student details

### Bus Management

- Bus number
- Driver name
- Route name
- Bus status
- Bus location

### Live Location

The system can obtain the current browser/device location and send:

- Latitude
- Longitude
- Speed

to the Flask backend.

The location is stored in the SQLite database.

### Estimated Arrival

The system displays estimated arrival information for the school bus.

### Notifications

The system provides bus-related notifications such as:

- Bus started from school
- Bus is currently on the route
- Estimated arrival time

### System Status

The dashboard displays:

- Online/Offline status
- Total buses
- Total students

---

## 5. Technology Stack

| Component | Technology |
|----------|------------|
| Frontend | HTML |
| Styling | CSS |
| Client-side Logic | JavaScript |
| Backend | Python Flask |
| Database | SQLite |
| API | REST API |
| Development Environment | Visual Studio Code |
| Version Control | Git / GitHub |

---

## 6. System Architecture

The application follows a simple three-layer architecture.

```text
User
  ↓
Frontend
HTML + CSS + JavaScript
  ↓
Flask REST API
  ↓
SQLite Database