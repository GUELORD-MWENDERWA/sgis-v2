from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QRCodeViewSet, MyQRCodeView, ValidateQRCodeData

router = DefaultRouter()
router.register(r'qrcodes', QRCodeViewSet, basename='qrcode')

urlpatterns = [
    path("", include(router.urls)),
    path("my/", MyQRCodeView.as_view(), name="my_qrcode"),
    path("validate/", ValidateQRCodeData.as_view(), name="validate_qrcode"),
]
