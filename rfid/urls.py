from django.urls import path
from .views import (
    CreateRFIDCard,
    ListAvailableRFIDCards,
    AssignRFIDCardToUser,
    CreateRFIDModule,
    ListRFIDModules,
    CheckRFIDModule,
)

urlpatterns = [
    # Cartes RFID
    path("cards/create/", CreateRFIDCard.as_view()),
    path("cards/available/", ListAvailableRFIDCards.as_view()),
    path("cards/assign/", AssignRFIDCardToUser.as_view()),

    # Modules RFID (matériel)
    path("modules/create/", CreateRFIDModule.as_view()),
    path("modules/", ListRFIDModules.as_view()),
    path("modules/check/", CheckRFIDModule.as_view()),   # pour ESP32
]
