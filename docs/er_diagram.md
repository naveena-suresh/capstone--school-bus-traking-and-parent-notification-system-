# School Bus Tracking System
## Entity Relationship (ER) Diagram

---

## 1. Database Overview

The School Bus Tracking System uses an SQLite database named:

`school_bus.db`

The database contains four main tables:

1. Users
2. Students
3. Buses
4. Bus Locations

---

## 2. ER Diagram

```mermaid
erDiagram

    USERS ||--o{ STUDENTS : "has"
    BUSES ||--o{ STUDENTS : "assigned to"
    BUSES ||--o{ BUS_LOCATIONS : "records"

    USERS {
        INTEGER user_id PK
        TEXT name
        TEXT email UK
        TEXT password
        TEXT role
    }

    STUDENTS {
        INTEGER student_id PK
        TEXT name
        INTEGER parent_id FK
        INTEGER bus_id FK
        TEXT stop_name
    }

    BUSES {
        INTEGER bus_id PK
        TEXT bus_number UK
        TEXT driver_name
        TEXT route_name
        TEXT status
        REAL latitude
        REAL longitude
    }

    BUS_LOCATIONS {
        INTEGER location_id PK
        INTEGER bus_id FK
        REAL latitude
        REAL longitude
        REAL speed
        TIMESTAMP recorded_at
    }