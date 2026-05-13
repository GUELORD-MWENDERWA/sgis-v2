# Module Attendance

## Description

Le module Attendance gère les sessions de présence et l'enregistrement des arrivées/départs des utilisateurs (principalement étudiants).

## Modèles

### AttendanceSession

- **Champs**:
  - `classroom`: ForeignKey vers ClassRoom
  - `school_year`: ForeignKey vers SchoolYear
  - `name`: CharField
  - `date`: DateField
  - `opened_at`: DateTimeField
  - `closed_at`: DateTimeField (nullable)
  - `is_open`: BooleanField
  - `limit_hour`, `limit_minute`: IntegerField (heure limite pour présent)

### Attendance

- **Champs**:
  - `session`: ForeignKey vers AttendanceSession
  - `user`: ForeignKey vers User
  - `student`: ForeignKey vers Student
  - `role`: CharField
  - `school_year`: ForeignKey vers SchoolYear
  - `classroom`: ForeignKey vers ClassRoom
  - `action`: CharField (IN/OUT)
  - `status`: CharField (PRESENT/LATE/UNKNOWN)
  - `reason`: CharField
  - `date`: DateField
  - `time`: TimeField
  - `entry_method`: CharField (QR/MANUAL/RFID)
  - `rfid_card`: ForeignKey vers RFIDCard
  - `recorded_by`: ForeignKey vers User
  - `note`: TextField
  - `created_at`: DateTimeField

## Fonctionnalités

- Sessions de présence par classe
- Enregistrement IN/OUT
- Calcul automatique du retard
- Support multiple méthodes d'entrée (QR, RFID, Manuel)
- Rapports de présence

## API Endpoints

- `GET /api/attendance/`: Liste des enregistrements
- `POST /api/attendance/`: Créer un enregistrement
- `GET /api/attendance/sessions/`: Sessions de présence
- `POST /api/attendance/sessions/`: Créer une session
- `POST /api/attendance/scan/`: Scan QR pour présence
- `POST /api/attendance/rfid/`: Scan RFID pour présence
- `GET /api/attendance/report/`: Rapport de présence

## Relations

- ForeignKey vers User, Student, ClassRoom, SchoolYear, RFIDCard
- Related name: `attendance_records`, `attendances`
