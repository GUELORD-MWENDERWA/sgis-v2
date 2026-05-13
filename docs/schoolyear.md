# Module SchoolYear

## Description

Le module SchoolYear gère les années scolaires du système. Chaque année scolaire a une période définie et une seule peut être active à la fois.

## Modèles

### SchoolYear

- **Champs**:
  - `name`: CharField unique (ex: "2024-2025")
  - `start_date`: DateField
  - `end_date`: DateField
  - `is_active`: BooleanField (une seule année active)

## Fonctionnalités

- Gestion des périodes scolaires
- Contrôle d'unicité de l'année active
- Association avec classes et étudiants

## API Endpoints

- `GET /api/schoolyear/`: Liste des années scolaires
- `POST /api/schoolyear/`: Créer une année scolaire
- `GET /api/schoolyear/{id}/`: Détails d'une année
- `PUT /api/schoolyear/{id}/`: Modifier une année
- `DELETE /api/schoolyear/{id}/`: Supprimer une année

## Relations

- ForeignKey dans Student, ClassRoom, AttendanceSession
- Related name: `students`, `classes`, `attendance_sessions`
