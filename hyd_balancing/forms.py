from django import forms
from .models import HeatingSystem, Room, Radiator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, ButtonHolder, HTML

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
                Submit('submit', 'Save System', css_class='btn btn-primary'),
                HTML('<a href="javascript:history.back()" class="btn btn-secondary ms-2">Cancel</a>')
            )
        )

class RoomForm(forms.ModelForm):
    length_m = forms.FloatField(required=False, label="Length (m)", min_value=0)
    width_m = forms.FloatField(required=False, label="Width (m)", min_value=0)

    class Meta:
        model = Room
        fields = ['name', 'length_m', 'width_m', 'area_sqm', 'height_m', 'target_temp', 'insulation_quality', 'custom_insulation_value']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['area_sqm'].required = False  # Make optional as it can be calculated
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Room Details',
                'name',
                Row(
                    Column('length_m', css_class='col-md-6'),
                    Column('width_m', css_class='col-md-6'),
                ),
                'area_sqm',
                Row(
                    Column('height_m', css_class='col-md-4'),
                    Column('target_temp', css_class='col-md-4'),
                ),
                Row(
                    Column('insulation_quality', css_class='col-md-6'),
                    Column('custom_insulation_value', css_class='col-md-6'),
                ),
            ),
            ButtonHolder(
                Submit('submit', 'Save Room', css_class='btn btn-primary'),
                HTML('<a href="javascript:history.back()" class="btn btn-secondary ms-2">Cancel</a>')
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        length = cleaned_data.get('length_m')
        width = cleaned_data.get('width_m')
        area = cleaned_data.get('area_sqm')
        insulation = cleaned_data.get('insulation_quality')
        custom_val = cleaned_data.get('custom_insulation_value')

        if not area and length and width:
            cleaned_data['area_sqm'] = length * width
        
        if not cleaned_data.get('area_sqm'):
            self.add_error('area_sqm', 'Please provide either the total area or length and width.')

        if insulation == 'custom' and not custom_val:
            self.add_error('custom_insulation_value', 'Please provide a custom value if you select "Custom".')
            
        return cleaned_data

class RadiatorForm(forms.ModelForm):
    class Meta:
        model = Radiator
        fields = ['name', 'radiator_type', 'width_mm', 'height_mm', 'area_sqm', 'pipe_length_m', 'load_percentage']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Radiator Specification',
                'name',
                Row(
                    Column('radiator_type', css_class='col-md-6'),
                    Column('load_percentage', css_class='col-md-6'),
                ),
                Row(
                    Column('area_sqm', css_class='col-md-6'),
                    Column('pipe_length_m', css_class='col-md-6'),
                ),
                Row(
                    Column('width_mm', css_class='col-md-6'),
                    Column('height_mm', css_class='col-md-6'),
                ),
            ),
            ButtonHolder(
                Submit('submit', 'Save Radiator', css_class='btn btn-primary'),
                HTML('<a href="javascript:history.back()" class="btn btn-secondary ms-2">Cancel</a>')
            )
        )

class RadiatorPercentageForm(forms.ModelForm):
    class Meta:
        model = Radiator
        fields = ['load_percentage']
        widgets = {
            'load_percentage': forms.NumberInput(attrs={'class': 'form-control percentage-input', 'min': 0, 'max': 100})
        }

from django.forms import modelformset_factory

RadiatorPercentageFormSet = modelformset_factory(
    Radiator,
    form=RadiatorPercentageForm,
    extra=0
)
