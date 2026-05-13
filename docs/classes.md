# Module Classes

## Description

Le module Classes gère les classes scolaires. Chaque classe appartient à une année scolaire et peut avoir un professeur principal et plusieurs enseignants.

## Modèles

### ClassRoom

- **Champs**:
  - `name`: CharField (ex: "6ème A")
  - `year`: ForeignKey vers SchoolYear
  - `main_teacher`: ForeignKey vers User (limit_choices_to TEACHER)
  - `teachers`: ManyToManyField vers User (limit_choices_to TEACHER)

## Fonctionnalités

- Organisation des élèves par classe
- Assignation d'enseignants
- Sessions de présence par classe

## API Endpoints

- `GET /api/classes/`: Liste des classes
- `POST /api/classes/`: Créer une classe
- `GET /api/classes/{id}/`: Détails d'une classe
- `PUT /api/classes/{id}/`: Modifier une classe
- `DELETE /api/classes/{id}/`: Supprimer une classe

## Relations

- ForeignKey dans Student (classroom)
- ForeignKey dans AttendanceSession (classroom)
- Related name: `classes_teaching`, `main_classes`
