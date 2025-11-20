from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    CreateStudentView, CreateParentView, CreateTeacherView,
    MeView, MeFullView, UpdateProfileView, ChangePasswordView,
    UploadProfilePhotoView, ListUsersView
)

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("me/", MeView.as_view(), name="me"),
    path("profile/update/", UpdateProfileView.as_view(), name="update_profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("upload/photo/", UploadProfilePhotoView.as_view(), name="upload_photo"),

    path("create/student/", CreateStudentView.as_view(), name="create_student"),
    path("create/parent/", CreateParentView.as_view(), name="create_parent"),
    path("create/teacher/", CreateTeacherView.as_view(), name="create_teacher"),

    path("list/", ListUsersView.as_view(), name="list_users"),
    path("me/full/", MeFullView.as_view(), name="me_full"),
]
