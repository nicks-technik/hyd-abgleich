from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class HeatingSystem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='systems', verbose_name=_("User"), null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name=_("System Name"))
    supply_temperature = models.IntegerField(default=70, verbose_name=_("Supply Temperature (°C)"), help_text=_("Vorlauftemperatur"))
    return_temperature = models.IntegerField(default=55, verbose_name=_("Return Temperature (°C)"), help_text=_("Rücklauftemperatur"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    INSULATION_CHOICES = [
        ('poor', _('Poor (Old Building)')),
        ('average', _('Average (Renovated)')),
        ('good', _('Good (Modern/Insulated)')),
        ('custom', _('Custom Value (W/m²)')),
    ]

    system = models.ForeignKey(HeatingSystem, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=100, verbose_name=_("Room Name"))
    area_sqm = models.FloatField(verbose_name=_("Area (m²)"))
    height_m = models.FloatField(default=2.5, verbose_name=_("Ceiling Height (m)"))
    target_temp = models.FloatField(default=20.0, verbose_name=_("Target Temperature (°C)"))
    insulation_quality = models.CharField(max_length=20, choices=INSULATION_CHOICES, default='average')
    custom_insulation_value = models.FloatField(null=True, blank=True, verbose_name=_("Custom Insulation Value (W/m²)"), help_text=_("Only used if 'Custom' is selected above"))

    def __str__(self):
        return f"{self.name} ({self.system.name})"

class Radiator(models.Model):
    TYPE_CHOICES = [
        ('10', 'Type 10'),
        ('11', 'Type 11'),
        ('21', 'Type 21'),
        ('22', 'Type 22'),
        ('33', 'Type 33'),
        ('underfloor', _('Underfloor Heating')),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='radiators')
    name = models.CharField(max_length=100, verbose_name=_("Radiator Identifier"), help_text=_("e.g. Window Left"))
    width_mm = models.IntegerField(verbose_name=_("Width (mm)"), null=True, blank=True)
    height_mm = models.IntegerField(verbose_name=_("Height (mm)"), null=True, blank=True)
    radiator_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='22')
    
    # Results (calculated later)
    calculated_load_watts = models.FloatField(null=True, blank=True, verbose_name=_("Calculated Load (W)"))
    required_flow_rate = models.FloatField(null=True, blank=True, verbose_name=_("Required Flow Rate (l/h)"))
    valve_setting = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Recommended Valve Setting"))

    def __str__(self):
        return f"{self.name} in {self.room.name}"