# API Documentation — CFCS v2.0 REST Endpoints

Base URL: `http://localhost:8000`

---

## Authentication API

### `POST /token`
- **Description**: Authenticate user and issue JWT Access Token.
- **Request Body** (`application/x-www-form-urlencoded`):
  - `username`: String
  - `password`: String
- **Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "token_type": "bearer"
}
```

---

## Face Recognition & Detection API

### `POST /api/recognize`
- **Description**: Process an uploaded face image and match against the criminal database.
- **Header**: `Authorization: Bearer <token>`
- **Form Data**: `file` (Image Upload)
- **Response**:
```json
{
  "match": true,
  "criminal_id": 1,
  "criminal_name": "Rajan Subramaniam",
  "confidence": 98.7,
  "threat_level": "Critical",
  "fir_number": "FIR-2024-001",
  "age_estimate": 38,
  "gender_estimate": "Male",
  "detection_id": 104
}
```

---

## Criminal Management API

### `GET /api/criminals`
- **Query Parameters**: `q` (search term), `threat` (filter), `status` (filter)
- **Response**: List of criminal objects.

### `POST /api/criminals`
- **Description**: Add new criminal record and train face recognizer on uploaded photo.
- **Form Data**: `name`, `alias`, `age`, `gender`, `fir_number`, `threat_level`, `case_status`, `photo`

### `GET /api/criminals/export/csv`
- **Description**: Download full criminal database in CSV format.

---

## Alert & Evidence Reporting API

### `GET /api/alerts`
- **Description**: Retrieve active and historical surveillance alerts.

### `PUT /api/alerts/{id}/resolve`
- **Description**: Mark alert as resolved.

### `GET /api/reports/pdf/{detection_id}`
- **Description**: Generate printable evidence report for court logging.

---

## ARIA AI Assistant API

### `POST /api/chat`
- **Description**: Query system via natural language prompt.
- **Request Body**: `{"message": "Show critical threat criminals"}`
- **Response**: Parsed intent & structured records.
