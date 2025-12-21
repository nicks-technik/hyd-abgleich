from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import HeatingSystem, Room, Radiator
from .forms import HeatingSystemForm, RoomForm, RadiatorForm

# --- Home/System List ---
class HomeView(ListView):
    model = HeatingSystem
    template_name = "hyd_balancing/home.html"
    context_object_name = 'systems'

class AboutView(TemplateView):
    template_name = "hyd_balancing/about.html"

# --- Heating System Views ---
class HeatingSystemCreateView(CreateView):
    model = HeatingSystem
    form_class = HeatingSystemForm
    template_name = 'hyd_balancing/system_form.html'
    
    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.pk})

class HeatingSystemDetailView(DetailView):
    model = HeatingSystem
    template_name = 'hyd_balancing/system_detail.html'
    context_object_name = 'system'

class HeatingSystemUpdateView(UpdateView):
    model = HeatingSystem
    form_class = HeatingSystemForm
    template_name = 'hyd_balancing/system_form.html'
    
    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.pk})

class HeatingSystemDeleteView(DeleteView):
    model = HeatingSystem
    template_name = 'hyd_balancing/system_confirm_delete.html'
    success_url = reverse_lazy('home')

# --- Room Views ---
class RoomCreateView(CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'hyd_balancing/room_form.html'

    def form_valid(self, form):
        system = get_object_or_404(HeatingSystem, pk=self.kwargs['system_pk'])
        form.instance.system = system
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['system'] = get_object_or_404(HeatingSystem, pk=self.kwargs['system_pk'])
        return context

    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.system.pk})

class RoomUpdateView(UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'hyd_balancing/room_form.html'

    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.system.pk})

class RoomDeleteView(DeleteView):
    model = Room
    template_name = 'hyd_balancing/room_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.system.pk})

# --- Radiator Views ---
class RadiatorCreateView(CreateView):
    model = Radiator
    form_class = RadiatorForm
    template_name = 'hyd_balancing/radiator_form.html'

    def form_valid(self, form):
        room = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        form.instance.room = room
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['room'] = get_object_or_404(Room, pk=self.kwargs['room_pk'])
        return context

    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.room.system.pk})

class RadiatorUpdateView(UpdateView):
    model = Radiator
    form_class = RadiatorForm
    template_name = 'hyd_balancing/radiator_form.html'

    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.room.system.pk})

class RadiatorDeleteView(DeleteView):
    model = Radiator
    template_name = 'hyd_balancing/radiator_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('system_detail', kwargs={'pk': self.object.room.system.pk})
