from rest_framework import serializers
from .models import SchoolYear

class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYear
        fields = ['id', 'name', 'start_date', 'end_date', 'is_active']

    def validate(self, data):
        """
        Vérifie qu'il n'y a qu'une seule année active.
        """
        if data.get('is_active'):
            qs = SchoolYear.objects.filter(is_active=True)
            # Si update, exclure l'instance existante
            if self.instance:
                qs = qs.exclude(id=self.instance.id)
            if qs.exists():
                raise serializers.ValidationError("Il y a déjà une année scolaire active.")
        return data
