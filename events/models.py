from django.conf import settings
from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return self.title

    @property
    def registered_count(self):
        return self.registrations.filter(status="active").count()

    @property
    def seats_left(self):
        return max(self.capacity - self.registered_count, 0)


class Registration(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("cancelled", "Cancelled")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registrations"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "event")  # ek user ek event me ek hi baar
        ordering = ["-registered_at"]

    def __str__(self):
        return f"{self.user} -> {self.event} ({self.status})"
