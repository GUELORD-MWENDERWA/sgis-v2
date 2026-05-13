# Module RFID

## Description

Le module RFID gère les cartes RFID physiques et les modules ESP32 pour l'identification automatique lors des prises de présence.

## Modèles

### RFIDCard

- **Champs**:
  - `uid`: CharField unique (identifiant de la carte)
  - `label`: CharField (étiquette optionnelle)
  - `notes`: TextField
  - `user`: OneToOneField vers User (nullable)
  - `created_at`, `updated_at`: DateTimeField

### RFIDModule

- **Champs**:
  - `name`: CharField (ex: "Entrée principale")
  - `location`: CharField (emplacement physique)
  - `token`: CharField unique (UUID pour authentification)
  - `notes`: TextField
  - `created_at`: DateTimeField

## Fonctionnalités

- Gestion des cartes RFID
- Assignation des cartes aux utilisateurs
- Authentification des modules ESP32
- Enregistrement automatique de présence via RFID

## API Endpoints

- `POST /api/rfid/cards/`: Créer une carte RFID
- `GET /api/rfid/cards/available/`: Cartes disponibles
- `POST /api/rfid/cards/assign/`: Assigner une carte à un utilisateur
- `POST /api/rfid/modules/`: Créer un module RFID
- `GET /api/rfid/modules/`: Lister les modules
- `POST /api/attendance/rfid/`: Enregistrer présence via RFID

## Relations

- OneToOne avec User (rfid_card)
- ForeignKey dans Attendance (rfid_card)
- Utilisé dans Attendance (entry_method = RFID)

## ESP32 Integration

Les modules ESP32 doivent envoyer des requêtes POST à `/api/attendance/rfid/` avec:

- `rfid_uid`: UID de la carte scannée
- `module_token`: Token du module ESP32
- Authentification JWT requise

### Développement séparé

Le développement du firmware ESP32 est prévu pour être fait séparément. La logique côté serveur Django reste inchangée et compatible avec l'implémentation ESP32.

### Flux ESP32

1. ESP32 scanne la carte RFID
2. Récupère l'UID de la carte
3. Envoie une requête HTTP POST authentifiée à l'API
4. Reçoit la réponse de validation de présence
