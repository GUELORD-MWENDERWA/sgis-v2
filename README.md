# SGIS - School Management Information System

## Vue d'ensemble

SGIS est un système de gestion scolaire complet développé avec Django REST Framework. Il permet de gérer les utilisateurs, les classes, les étudiants, les années scolaires, et les présences via différents moyens (QR codes, RFID, manuel).

## Architecture

Le projet est organisé en modules Django indépendants :

- **accounts**: Gestion des utilisateurs et authentification
- **schoolyear**: Gestion des années scolaires
- **classes**: Gestion des classes et enseignants
- **students**: Profils étudiants et inscriptions
- **qrcodes**: Génération et gestion des codes QR
- **rfid**: Gestion des cartes RFID et modules ESP32
- **attendance**: Sessions et enregistrements de présence

## Technologies utilisées

- **Backend**: Django 5.2, Django REST Framework
- **Authentification**: JWT (JSON Web Tokens)
- **Base de données**: SQLite (dev), PostgreSQL (prod)
- **Déploiement**: Heroku/Render
- **Hardware**: ESP32 pour RFID

## Installation et configuration

### Prérequis

- Python 3.8+
- pip
- virtualenv

### Installation

```bash
git clone <repository>
cd sgis
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Variables d'environnement

Créer un fichier `.env` :

```
SECRET_KEY=votre_secret_key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

## API Documentation

### Authentification

Toutes les requêtes API nécessitent un token JWT dans le header :

```
Authorization: Bearer <token>
```

### Endpoints principaux

- `POST /api/auth/login/`: Connexion
- `GET /api/schoolyear/`: Années scolaires
- `GET /api/classes/`: Classes
- `GET /api/students/`: Étudiants
- `POST /api/attendance/scan/`: Enregistrer présence (QR)
- `POST /api/attendance/rfid/`: Enregistrer présence (RFID)

## Flux de présence

### Via QR Code

1. L'utilisateur scanne son QR code
2. L'app mobile/web envoie le token à `/api/attendance/scan/`
3. Le système enregistre IN/OUT selon l'état actuel

### Via RFID

1. L'ESP32 détecte une carte RFID
2. L'ESP32 envoie `rfid_uid` et `module_token` à `/api/attendance/rfid/`
3. Le système enregistre la présence automatiquement

### Manuellement

1. L'enseignant/admin enregistre via l'interface
2. Utilise `POST /api/attendance/` avec `entry_method: "MANUAL"`

## Développement ESP32

Le module RFID est conçu pour être développé séparément sur ESP32. La logique côté serveur reste la même :

- Authentification via `module_token`
- Envoi de `rfid_uid` scanné
- Réponse avec statut de l'enregistrement

### Exemple code ESP32 (pseudo-code)

```cpp
// Connexion WiFi
// Lecture RFID
String uid = readRFID();
// Envoi HTTP POST
HTTPClient http;
http.begin("https://api.sgis.com/api/attendance/rfid/");
http.addHeader("Authorization", "Bearer " + jwt_token);
http.addHeader("Content-Type", "application/json");
String payload = "{\"rfid_uid\":\"" + uid + "\", \"module_token\":\"" + module_token + "\"}";
int response = http.POST(payload);
```

## Base de données

Le schéma relationnel lie tous les modules :

- User → Student (1:1)
- SchoolYear → Student, ClassRoom (1:N)
- ClassRoom → Student, AttendanceSession (1:N)
- RFIDCard → User (1:1)
- Attendance → User, Student, ClassRoom, RFIDCard (N:1)

## Sécurité

- Authentification JWT obligatoire
- Permissions par rôle (admin, teacher, student)
- Validation des données d'entrée
- Logs d'audit pour les présences

## Tests

```bash
python manage.py test
```

## Déploiement

Le projet est configuré pour Heroku/Render avec :

- `Procfile`
- `render.yaml`
- Variables d'environnement
- Base de données PostgreSQL

## Modules détaillés

Voir la documentation détaillée dans `docs/` :

- [Accounts](docs/accounts.md)
- [SchoolYear](docs/schoolyear.md)
- [Classes](docs/classes.md)
- [Students](docs/students.md)
- [QRCodes](docs/qrcodes.md)
- [RFID](docs/rfid.md)
- [Attendance](docs/attendance.md)

## Contribution

1. Fork le projet
2. Créer une branche feature
3. Commiter les changements
4. Push et créer une PR

## Licence

MIT License
