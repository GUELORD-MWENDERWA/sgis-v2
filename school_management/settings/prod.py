from .base import *

DEBUG = False
ALLOWED_HOSTS = ["*"]  # ou ton domaine personnalisé

# PostgreSQL Render via DATABASE_URL
# Base déjà configurée dans base.py via dj_database_url

# CORS pour ton frontend
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",          # Frontend local
    "http://192.168.1.50",            # IP locale de l’ESP32CAM
    "https://ton-frontend.com",       # à remplacer plus tard par ton vrai domaine
]

# Sécurité HTTPS / cookies
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
