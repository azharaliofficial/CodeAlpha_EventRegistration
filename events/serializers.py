from rest_framework import serializers

from .models import Event, Registration


class EventSerializer(serializers.ModelSerializer):
    seats_left = serializers.IntegerField(read_only=True)
    is_registered = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ["id", "title", "description", "date", "location",
                  "capacity", "seats_left", "is_registered"]

    def get_is_registered(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.registrations.filter(user=request.user, status="active").exists()
        return False


class RegistrationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Registration
        fields = ["id", "event", "status", "registered_at"]
