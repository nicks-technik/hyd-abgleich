from django.urls import path
from .views import (
    HomeView, AboutView,
    HeatingSystemCreateView, HeatingSystemDetailView, HeatingSystemUpdateView, HeatingSystemDeleteView, HeatingSystemCalculateView,
    RoomCreateView, RoomUpdateView, RoomDeleteView, RoomRadiatorPercentageView,
    RadiatorCreateView, RadiatorUpdateView, RadiatorDeleteView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    
    # Heating System URLs
    path('system/add/', HeatingSystemCreateView.as_view(), name='system_create'),
    path('system/<int:pk>/', HeatingSystemDetailView.as_view(), name='system_detail'),
    path('system/<int:pk>/edit/', HeatingSystemUpdateView.as_view(), name='system_update'),
    path('system/<int:pk>/delete/', HeatingSystemDeleteView.as_view(), name='system_delete'),
    path('system/<int:pk>/calculate/', HeatingSystemCalculateView.as_view(), name='system_calculate'),

    # Room URLs
    path('system/<int:system_pk>/room/add/', RoomCreateView.as_view(), name='room_create'),
    path('room/<int:pk>/edit/', RoomUpdateView.as_view(), name='room_update'),
    path('room/<int:pk>/delete/', RoomDeleteView.as_view(), name='room_delete'),

    # Radiator URLs
    path('room/<int:room_pk>/radiator/add/', RadiatorCreateView.as_view(), name='radiator_create'),
    path('radiator/<int:pk>/edit/', RadiatorUpdateView.as_view(), name='radiator_update'),
    path('radiator/<int:pk>/delete/', RadiatorDeleteView.as_view(), name='radiator_delete'),
    path('room/<int:pk>/percentages/', RoomRadiatorPercentageView.as_view(), name='room_radiator_percentages'),
]