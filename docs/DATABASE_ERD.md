# Database Schema & Entity Relationship — CFCS v2.0

## Entity Relationship Summary

The database is built on SQLAlchemy with SQLite / PostgreSQL support. It models administrators, authorized personnel, criminal database records, surveillance camera feeds, detection event logs, alert notifications, and ARIA AI query sessions.

```mermaid
erDiagram
    ADMIN {
        int id PK
        string username
        string hashed_password
        string role
        string full_name
        datetime created_at
    }

    CRIMINAL {
        int id PK
        string name
        string alias
        int age
        string gender
        string fir_number
        string crime_history
        string case_status
        string threat_level
        string last_seen_location
        string nationality
        string address
        string image_path
        float latitude
        float longitude
        datetime created_at
    }

    CAMERA {
        int id PK
        string name
        string location
        string ip_address
        string status
        string camera_type
        float latitude
        float longitude
    }

    DETECTION_LOG {
        int id PK
        int criminal_id FK
        string criminal_name
        int camera_id FK
        string camera_location
        float confidence
        string threat_level
        string screenshot_path
        int age_estimate
        string gender_estimate
        boolean is_unknown
        string status
        datetime detected_at
    }

    ALERT_LOG {
        int id PK
        int detection_id FK
        int criminal_id FK
        string criminal_name
        string alert_type
        string severity
        string message
        boolean is_resolved
        datetime created_at
    }

    CRIMINAL ||--o{ DETECTION_LOG : "triggers"
    CAMERA ||--o{ DETECTION_LOG : "captures"
    DETECTION_LOG ||--o{ ALERT_LOG : "generates"
```

## Table Definitions

### 1. `admins`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | Integer | Primary Key | Unique user ID |
| `username` | String | Unique, Indexed | Account login ID |
| `hashed_password` | String | Not Null | Bcrypt hashed passkey |
| `role` | String | Default: 'admin' | admin / officer / investigator / operator |
| `full_name` | String | Not Null | Officer full name |

### 2. `criminals`
| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary Key |
| `name` | String | Primary criminal full name |
| `alias` | String | Known street alias |
| `fir_number` | String | Unique FIR Police Case # |
| `threat_level` | String | Low / Medium / High / Critical |
| `case_status` | String | Active / Wanted / Arrested / Closed |
| `latitude` / `longitude` | Float | Spatial coordinate for heatmap |

### 3. `detection_logs`
| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer | Primary Key |
| `criminal_id` | Integer | FK to `criminals.id` (NULL if unknown) |
| `confidence` | Float | Face match confidence % (e.g. 98.5) |
| `screenshot_path` | String | Local file path to captured frame |
| `detected_at` | DateTime | Timestamp of event |
