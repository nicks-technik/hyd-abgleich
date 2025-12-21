from django.urls import path
from .views import (
    HomeView,
    HeatingSystemCreateView, HeatingSystemDetailView, HeatingSystemUpdateView, HeatingSystemDeleteView,
    RoomCreateView, RoomUpdateView, RoomDeleteView,
    RadiatorCreateView, RadiatorUpdateView, RadiatorDeleteView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    
    # Heating System URLs
    path('system/add/', HeatingSystemCreateView.as_view(), name='system_create'),
    path('system/<int:pk>/', HeatingSystemDetailView.as_view(), name='system_detail'),
    path('system/<int:pk>/edit/', HeatingSystemUpdateView.as_view(), name='system_update'),
    path('system/<int:pk>/delete/', HeatingSystemDeleteView.as_view(), name='system_delete'),

    # Room URLs
    path('system/<int:system_pk>/room/add/', RoomCreateView.as_view(), name='room_create'),
    path('room/<int:pk>/edit/', RoomUpdateView.as_view(), name='room_update'),
    path('room/<int:pk>/delete/', RoomDeleteView.as_view(), name='room_delete'),

    # Radiator URLs
    path('room/<int:room_pk>/radiator/add/', RadiatorCreateView.as_view(), name='radiator_create'),
    path('radiator/<int:pk>/edit/', RadiatorUpdateView.as_view(), name='radiator_update'),
    path('radiator/<int:pk>/delete/', RadiatorDeleteView.as_view(), name='radiator_delete'),
]