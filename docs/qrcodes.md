# Module QRCodes

## Description

Le module QRCodes génère et gère les codes QR pour l'identification des utilisateurs lors des prises de présence.

## Modèles

### QRCode

- **Champs**:
  - `user`: OneToOneField vers User
  - `code`: UUIDField unique (token sécurisé)
  - `code_image`: ImageField (image PNG générée)
  - `created_at`: DateTimeField

## Fonctionnalités

- Génération automatique de codes QR uniques
- Stockage des images QR
- Scan pour enregistrement de présence

## API Endpoints

- `GET /api/qrcode/generate/`: Générer un QR pour l'utilisateur connecté
- `GET /api/qrcode/{user_id}/`: Obtenir le QR d'un utilisateur
- `POST /api/attendance/scan/`: Scanner un QR pour présence

## Relations

- OneToOne avec User (qr_code)
- Utilisé dans Attendance (entry_method = QR)
