from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class HeatingSystem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='systems', verbose_name=_("User"), null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name=_("System Name"), help_text=_("A name to identify this house or apartment."))
    supply_temperature = models.IntegerField(default=70, verbose_name=_("Supply Temperature (°C)"), help_text=_("The temperature of the water leaving the boiler (Vorlauftemperatur). Higher values are common in older buildings."))
    return_temperature = models.IntegerField(default=55, verbose_name=_("Return Temperature (°C)"), help_text=_("The temperature of the water returning to the boiler (Rücklauftemperatur). The difference to supply temp affects flow rates."))
    max_valve_setting = models.IntegerField(default=6, verbose_name=_("Max Valve Setting"), help_text=_("The maximum setting value for the thermostat valves (usually 6, sometimes 10 or 15)."))
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
    name = models.CharField(max_length=100, verbose_name=_("Room Name"), help_text=_("e.g. Living Room, Bedroom 1"))
    floor = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Floor"), help_text=_("e.g., Ground Floor, 1st Floor"))
    area_sqm = models.FloatField(verbose_name=_("Area (m²)"), help_text=_("Total floor area of the room. Can be calculated from length and width."))
    height_m = models.FloatField(default=2.5, verbose_name=_("Ceiling Height (m)"), help_text=_("The vertical height of the room, used for volume estimations."))
    external_walls = models.IntegerField(default=1, verbose_name=_("External Walls"), help_text=_("Number of walls facing outside (0-4). Affects heat demand."))
    target_temp = models.FloatField(default=20.0, verbose_name=_("Target Temperature (°C)"), help_text=_("Desired room temperature. Usually 20°C for living rooms, 22°C for bathrooms."))
    insulation_quality = models.CharField(max_length=20, choices=INSULATION_CHOICES, default='average', help_text=_("Affects how much heat (W/m²) is needed to maintain temperature."))
    custom_insulation_value = models.FloatField(null=True, blank=True, verbose_name=_("Custom Insulation Value (W/m²)"), help_text=_("Specify the exact heat demand in Watts per square meter."))

    def __str__(self):
        return f"{self.name} ({self.system.name})"

    @property
    def total_load_percentage(self):
        return sum(rad.load_percentage for rad in self.radiators.all())

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
    name = models.CharField(max_length=100, verbose_name=_("Radiator Identifier"), help_text=_("e.g. Window Left, North Wall. Helps you identify the valve to adjust."))
    width_mm = models.IntegerField(verbose_name=_("Width (mm)"), null=True, blank=True, help_text=_("Width of the radiator in millimeters. Not needed for underfloor heating."))
    height_mm = models.IntegerField(verbose_name=_("Height (mm)"), null=True, blank=True, help_text=_("Height of the radiator in millimeters. Not needed for underfloor heating."))
    area_sqm = models.FloatField(verbose_name=_("Area (m²)"), null=True, blank=True, help_text=_("For underfloor heating: The floor area covered by this specific heating loop."))
    pipe_length_m = models.IntegerField(verbose_name=_("Pipe Length (m)"), null=True, blank=True, help_text=_("Total length of the heating pipe in this loop."))
    radiator_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='22', help_text=_("Type determines heat output. 22 is the most common double-panel radiator."))
    load_percentage = models.IntegerField(default=100, verbose_name=_("Load Percentage (%)"), help_text=_("Percentage of the room's total heat load this radiator should cover. Total for all radiators in a room should be 100%."))
    
    # Results (calculated later)
    nominal_capacity_watts = models.FloatField(null=True, blank=True, verbose_name=_("Nominal Power (W)"), help_text=_("Power at standard 75/65/20 temperatures."))
    max_capacity_watts = models.FloatField(null=True, blank=True, verbose_name=_("Max Capacity (W)"))
    calculated_load_watts = models.FloatField(null=True, blank=True, verbose_name=_("Calculated Load (W)"), help_text=_("The heat energy this specific radiator must deliver."))
    required_flow_rate = models.FloatField(null=True, blank=True, verbose_name=_("Required Flow Rate (l/h)"), help_text=_("The amount of water that should pass through the valve per hour."))
    valve_setting = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Recommended Valve Setting"), help_text=_("The pre-setting to apply to your radiator valve."))

    def __str__(self):
        return f"{self.name} in {self.room.name}"

    @property
    def flow_calculation_details(self):
        if not self.required_flow_rate or not self.calculated_load_watts:
            return None
        
        is_ufh = self.radiator_type == 'underfloor'
        sys = self.room.system
        dt = 7.0 if is_ufh else (sys.supply_temperature - sys.return_temperature)
        if dt <= 0: dt = 15.0
        
        return {
            'load': self.calculated_load_watts,
            'delta_t': dt,
            'constant': 1.163,
            'formula': "Flow = Load / (1.163 * ΔT)",
            'explanation': f"The heat load ({self.calculated_load_watts}W) is divided by the water constant (1.163) and the temperature spread ({dt}K).",
            'full_string': f"{self.calculated_load_watts} / (1.163 * {dt}) = {self.required_flow_rate} l/h"
        }
    