from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import HeatingSystem, Room, Radiator
from .forms import HeatingSystemForm, RoomForm, RadiatorForm, RadiatorPercentageFormSet
from .calculation import perform_hydraulic_balancing

# ... existing views ...

class RoomRadiatorPercentageView(LoginRequiredMixin, View):
    template_name = 'hyd_balancing/room_percentages.html'

    def get(self, request, pk):
        room = get_object_or_404(Room, pk=pk, system__user=request.user)
        formset = RadiatorPercentageFormSet(queryset=room.radiators.all())
        return render(request, self.template_name, {'room': room, 'formset': formset})

    def post(self, request, pk):
        room = get_object_or_404(Room, pk=pk, system__user=request.user)
        radiators = room.radiators.all()
        
        if 'auto_distribute' in request.POST:
            total_capacity = sum(rad.max_capacity_watts or 0 for rad in radiators)
            if total_capacity > 0:
                for rad in radiators:
                    percentage = round(((rad.max_capacity_watts or 0) / total_capacity) * 100)
                    rad.load_percentage = percentage
                    rad.save()
                messages.success(request, "Percentages automatically distributed based on radiator capacities.")
            else:
                messages.error(request, "Cannot auto-distribute: Radiator capacities are 0. Please run calculations first.")
            return redirect('room_radiator_percentages', pk=pk)

        formset = RadiatorPercentageFormSet(request.POST, queryset=radiators)
        if formset.is_valid():
            # Check total percentage
            total = sum(form.cleaned_data.get('load_percentage', 0) for form in formset)
            if total > 100:
                messages.error(request, f"Total percentage cannot exceed 100% (Current total: {total}%).")
                return render(request, self.template_name, {'room': room, 'formset': formset})
            
            formset.save()
            messages.success(request, f"Percentages updated for {room.name}.")
            return redirect('system_detail', pk=room.system.pk)
        return render(request, self.template_name, {'room': room, 'formset': formset})

# --- Home/System List ---
class HomeView(LoginRequiredMixin, ListView):
    model = HeatingSystem
    template_name = "hyd_balancing/home.html"
    context_object_name = 'systems'

    def get_queryset(self):
        return HeatingSystem.objects.filter(user=self.request.user)

class AboutView(View):
    def get(self, request):
        return render(request, "hyd_balancing/about.html")

# --- Heating System Views ---
class HeatingSystemCreateView(LoginRequiredMixin, CreateView):
    model = HeatingSystem
    form_class = HeatingSystemForm
    template_name = 'hyd_balancing/system_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.pk})

class HeatingSystemDetailView(LoginRequiredMixin, DetailView):
    model = HeatingSystem
    template_name = 'hyd_balancing/system_detail.html'
    context_object_name = 'system'

    def get_queryset(self):
        return HeatingSystem.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system = self.object
        rooms = system.rooms.all()
        
        total_area = 0
        total_load = 0
        total_radiators = 0
        
        # We need the logic from calculation.py to show stats
        from .calculation import get_specific_heat_demand
        
        for room in rooms:
            total_area += room.area_sqm
            specific_heat = get_specific_heat_demand(room)
            total_load += room.area_sqm * specific_heat
            total_radiators += room.radiators.count()
            
        context['total_area'] = round(total_area, 2)
        context['total_load_kw'] = round(total_load / 1000, 2)
        context['total_radiators'] = total_radiators
        context['delta_t'] = system.supply_temperature - system.return_temperature
        return context

class HeatingSystemUpdateView(LoginRequiredMixin, UpdateView):
    model = HeatingSystem
    form_class = HeatingSystemForm
    template_name = 'hyd_balancing/system_form.html'
    
    def get_queryset(self):
        return HeatingSystem.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.pk})

class HeatingSystemDeleteView(LoginRequiredMixin, DeleteView):
    model = HeatingSystem
    template_name = 'hyd_balancing/system_confirm_delete.html'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        return HeatingSystem.objects.filter(user=self.request.user)

class HeatingSystemCalculateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        system = get_object_or_404(HeatingSystem, pk=pk, user=request.user)
        perform_hydraulic_balancing(system)
        messages.success(request, f"Calculation completed for {system.name}.")
        return redirect('system_detail', pk=pk)

# --- Room Views ---
class RoomCreateView(LoginRequiredMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'hyd_balancing/room_form.html'

    def form_valid(self, form):
        system = get_object_or_404(HeatingSystem, pk=self.kwargs['system_pk'], user=self.request.user)
        form.instance.system = system
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['system'] = get_object_or_404(HeatingSystem, pk=self.kwargs['system_pk'], user=self.request.user)
        return context

    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.system.pk})

class RoomUpdateView(LoginRequiredMixin, UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'hyd_balancing/room_form.html'

    def get_queryset(self):
        return Room.objects.filter(system__user=self.request.user)

    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.system.pk})

class RoomDeleteView(LoginRequiredMixin, DeleteView):
    model = Room
    template_name = 'hyd_balancing/room_confirm_delete.html'
    
    def get_queryset(self):
        return Room.objects.filter(system__user=self.request.user)

    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.system.pk})

# --- Radiator Views ---
class RadiatorCreateView(LoginRequiredMixin, CreateView):
    model = Radiator
    form_class = RadiatorForm
    template_name = 'hyd_balancing/radiator_form.html'

    def form_valid(self, form):
        room = get_object_or_404(Room, pk=self.kwargs['room_pk'], system__user=self.request.user)
        form.instance.room = room
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room'] = get_object_or_404(Room, pk=self.kwargs['room_pk'], system__user=self.request.user)
        return context

    def get_success_url(self):
        room = self.object.room
        if room.radiators.count() > 1:
            return reverse('room_radiator_percentages', kwargs={'pk': room.pk})
        return reverse('system_detail', kwargs={'pk': room.system.pk})

class RadiatorUpdateView(LoginRequiredMixin, UpdateView):
    model = Radiator
    form_class = RadiatorForm
    template_name = 'hyd_balancing/radiator_form.html'

    def get_queryset(self):
        return Radiator.objects.filter(room__system__user=self.request.user)

    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.room.system.pk})

class RadiatorDeleteView(LoginRequiredMixin, DeleteView):
    model = Radiator
    template_name = 'hyd_balancing/radiator_confirm_delete.html'
    
    def get_queryset(self):
        return Radiator.objects.filter(room__system__user=self.request.user)

    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.room.system.pk})
