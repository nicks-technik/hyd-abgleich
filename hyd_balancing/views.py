from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import HeatingSystem, Room, Radiator
from .forms import HeatingSystemForm, RoomForm, RadiatorForm
from .calculation import perform_hydraulic_balancing

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
        return reverse('system_detail', kwargs={'pk': self.object.room.system.pk})

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
