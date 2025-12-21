from django import forms
from .models import HeatingSystem, Room, Radiator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, ButtonHolder

class HeatingSystemForm(forms.ModelForm):
    class Meta:
        model = HeatingSystem
        fields = ['name', 'supply_temperature', 'return_temperature']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Heating System Parameters',
                'name',
                Row(
                    Column('supply_temperature', css_class='form-group col-md-6 mb-0'),
                    Column('return_temperature', css_class='form-group col-md-6 mb-0'),
                    css_class='row'
                ),
            ),
            ButtonHolder(
                Submit('submit', 'Save System', css_class='btn btn-primary')
            )
        )

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'area_sqm', 'height_m', 'target_temp', 'insulation_quality']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Room Details',
                'name',
                Row(
                    Column('area_sqm', css_class='col-md-6'),
                    Column('height_m', css_class='col-md-6'),
                ),
                Row(
                    Column('target_temp', css_class='col-md-6'),
                    Column('insulation_quality', css_class='col-md-6'),
                ),
            ),
            ButtonHolder(
                Submit('submit', 'Save Room', css_class='btn btn-primary')
            )
        )

class RadiatorForm(forms.ModelForm):
    class Meta:
        model = Radiator
        fields = ['name', 'radiator_type', 'width_mm', 'height_mm']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Radiator Specification',
                'name',
                'radiator_type',
                Row(
                    Column('width_mm', css_class='col-md-6'),
                    Column('height_mm', css_class='col-md-6'),
                ),
            ),
            ButtonHolder(
                Submit('submit', 'Save Radiator', css_class='btn btn-primary')
            )
        )
