from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Event, Registration
from .serializers import EventSerializer, RegistrationSerializer


def home(request):
    """Frontend page."""
    return render(request, "index.html")


# ---------- Auth ----------
@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    username = (request.data.get("username") or "").strip()
    password = request.data.get("password") or ""
    if not username or not password:
        return Response({"error": "Username and password are required."}, status=400)
    if len(password) < 6:
        return Response({"error": "Password must be at least 6 characters."}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken."}, status=400)
    user = User.objects.create_user(username=username, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username}, status=201)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    user = authenticate(
        username=request.data.get("username"), password=request.data.get("password")
    )
    if user is None:
        return Response({"error": "Wrong username or password."}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username})


# ---------- Events ----------
@api_view(["GET"])
@permission_classes([AllowAny])
def event_list(request):
    events = Event.objects.all()
    return Response(EventSerializer(events, many=True, context={"request": request}).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return Response(EventSerializer(event, context={"request": request}).data)


# ---------- Registrations ----------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_for_event(request, event_id):
    with transaction.atomic():
        event = get_object_or_404(Event.objects.select_for_update(), pk=event_id)
        existing = Registration.objects.filter(user=request.user, event=event).first()

        if existing and existing.status == "active":
            return Response({"error": "You are already registered for this event."}, status=400)
        if event.seats_left <= 0:
            return Response({"error": "This event is full."}, status=400)

        if existing:  # pehle cancel kiya tha, dobara active karo
            existing.status = "active"
            existing.save()
            registration = existing
        else:
            registration = Registration.objects.create(user=request.user, event=event)

    return Response(RegistrationSerializer(registration, context={"request": request}).data,
                    status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_registrations(request):
    regs = Registration.objects.filter(user=request.user, status="active")
    return Response(RegistrationSerializer(regs, many=True, context={"request": request}).data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cancel_registration(request, registration_id):
    # sirf apni registration cancel ho sakti hai
    reg = get_object_or_404(Registration, pk=registration_id, user=request.user)
    reg.status = "cancelled"
    reg.save()
    return Response({"message": "Registration cancelled."})
