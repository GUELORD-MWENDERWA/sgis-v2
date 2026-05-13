# Module Accounts

## Description

Le module Accounts gère la gestion des utilisateurs du système SGIS (School Management Information System). Il étend le modèle User de Django avec des rôles spécifiques et des informations supplémentaires.

## Modèles

### User

- **Héritage**: AbstractUser de Django
- **Rôles disponibles**:
  - ADMIN: Administrateur
  - STAFF: Personnel
  - TEACHER: Enseignant
  - PARENT: Parent
  - STUDENT: Étudiant
- **Champs supplémentaires**:
  - `role`: CharField avec choix des rôles
  - `photo`: ImageField pour la photo de profil
  - `matricule`: CharField unique pour l'identifiant étudiant/personnel
  - `phone`: CharField pour le numéro de téléphone
  - `birth_date`: DateField pour la date de naissance

## Fonctionnalités

- Authentification JWT
- Gestion des rôles utilisateur
- Upload de photos de profil
- Génération automatique de matricules

## API Endpoints

- `POST /api/auth/register/`: Inscription
- `POST /api/auth/login/`: Connexion
- `GET /api/auth/profile/`: Profil utilisateur
- `PUT /api/auth/profile/`: Mise à jour du profil

## Relations

- OneToOne avec Student (si rôle STUDENT)
- ManyToMany avec Student (parents)
- ForeignKey dans diverses entités (enseignants, etc.)
