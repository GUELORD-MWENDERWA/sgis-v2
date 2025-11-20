from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrTeacherOrOwner(BasePermission):
    """
    Permissions pour l'Attendance :

    - Admin : accès complet (CRUD total)
    - Teacher : peut lire/lister + scanner les élèves de sa classe
    - Student : accès uniquement à ses propres enregistrements
    - Parent : accès uniquement si un motif (reason) est renseigné
    """

    def has_permission(self, request, view):
        # L'utilisateur doit être authentifié
        if not request.user or not request.user.is_authenticated:
            return False

        # Méthodes sûres (GET, HEAD, OPTIONS) accessibles
        if request.method in SAFE_METHODS:
            return True

        # POST (scanner QR) autorisé pour tous les rôles
        if request.method == 'POST':
            return True

        # Pour PUT, PATCH, DELETE → seul l'ADMIN est autorisé
        return request.user.role == 'ADMIN'

    def has_object_permission(self, request, view, obj):
        # Admin → toujours autorisé
        if request.user.role == 'ADMIN':
            return True

        # Teacher → accès si la classe correspond
        if request.user.role == 'TEACHER':
            if obj.classroom and obj.classroom.main_teacher_id == request.user.id:
                return True

        # Student → accès uniquement à ses propres enregistrements
        if request.user.role == 'STUDENT':
            return obj.user == request.user

        # Parent → accès uniquement si un motif est renseigné
        if request.user.role == 'PARENT':
            return bool(obj.reason)

        return False
