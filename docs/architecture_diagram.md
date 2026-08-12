# School Bus Tracking System
## System Architecture Diagram

---

## 1. Overview

The School Bus Tracking System is a web-based application designed to
manage student details, bus details, driver information and live bus
location.

The system uses:

- Frontend: HTML, CSS and JavaScript
- Backend: Python Flask
- Database: SQLite
- Communication: REST API
- Location: Latitude and Longitude
- ETA: Estimated Arrival Time
- Notifications: Bus status and arrival messages

---

## 2. System Architecture

```mermaid
flowchart TD

    USER["Parent / School Admin"]

    FRONTEND["Frontend
    HTML + CSS + JavaScript"]

    API["Flask Backend
    app.py"]

    DATABASE["SQLite Database
    school_bus.db"]

    USERS["Users Table"]
    STUDENTS["Students Table"]
    BUSES["Buses Table"]
    LOCATIONS["Bus Locations Table"]

    LOCATION["Live GPS Location"]

    ETA["ETA Service"]

    NOTIFICATION["Notification Service"]

    USER --> FRONTEND

    FRONTEND -->|"HTTP Requests"| API

    API -->|"Read / Write"| DATABASE

    DATABASE --> USERS
    DATABASE --> STUDENTS
    DATABASE --> BUSES
    DATABASE --> LOCATIONS

    LOCATION -->|"Latitude / Longitude / Speed"| API

    API --> ETA
    API --> NOTIFICATION

    API -->|"JSON Response"| FRONTEND

    FRONTEND -->|"Display"| USER