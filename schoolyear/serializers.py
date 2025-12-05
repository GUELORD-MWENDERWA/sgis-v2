from rest_framework import serializers
from .models import SchoolYear

class SchoolYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYear
        fields = ['id', 'name', 'start_date', 'end_date', 'is_active']

    def validate(self, data):
        """
        Vérifie qu'il n'y a qu'une seule année scolaire active à la fois.
        """
        is_active = data.get('is_active', getattr(self.instance, 'is_active', False))
        if is_active:
            qs = SchoolYear.objects.filter(is_active=True)
            # Si on update une instance existante, exclure cette instance
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("Il y a déjà une année scolaire active.")
        return data
