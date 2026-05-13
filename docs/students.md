# Module Students

## Description

Le module Students gère les profils étudiants. Chaque étudiant est lié à un utilisateur et peut être inscrit dans une classe pour une année scolaire donnée.

## Modèles

### Student

- **Champs**:
  - `user`: OneToOneField vers User
  - `school_year`: ForeignKey vers SchoolYear
  - `classroom`: ForeignKey vers ClassRoom (nullable)
  - `parents`: ManyToManyField vers User (limit_choices_to PARENT)

## Fonctionnalités

- Profil étudiant lié au compte utilisateur
- Inscription annuelle dans une classe
- Gestion des parents
- Suivi des présences

## API Endpoints

- `GET /api/students/`: Liste des étudiants
- `POST /api/students/`: Créer un profil étudiant
- `GET /api/students/{id}/`: Détails d'un étudiant
- `PUT /api/students/{id}/`: Modifier un profil étudiant
- `DELETE /api/students/{id}/`: Supprimer un profil étudiant

## Relations

- OneToOne avec User (student_profile)
- ForeignKey dans Attendance (student)
- ManyToMany avec User (children pour les parents)
