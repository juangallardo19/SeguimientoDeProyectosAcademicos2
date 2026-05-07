from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView, UpdateView, DeleteView
from django.utils import timezone
from django.http import HttpResponseForbidden
from .forms import DocenteProyectoForm
from .models import Comentario
from .forms import ComentarioForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('proyecto-list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('proyecto-list')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'Ejercicio2App/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def es_docente(user):
    return user.groups.filter(name='docente').exists() or user.is_staff


def es_estudiante(user):
    return user.groups.filter(name='estudiante').exists()

class ProyectoListView(LoginRequiredMixin, ListView):
    model = Proyecto
    template_name = 'Ejercicio2App/proyecto_list.html'
    context_object_name = 'proyectos'
    paginate_by = 10

    def get_queryset(self):
        qs = Proyecto.objects.select_related('estudiante')
        if not es_docente(self.request.user):
            qs = qs.filter(estudiante=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['es_docente'] = es_docente(self.request.user)
        ctx['total'] = self.get_queryset().count()
        return ctx


class ProyectoCreateView(LoginRequiredMixin, CreateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = 'Ejercicio2App/proyecto_form.html'
    success_url = reverse_lazy('proyecto-list')

    def dispatch(self, request, *args, **kwargs):
        if es_docente(request.user):
            messages.error(request, 'Los docentes no pueden crear proyectos.')
            return redirect('proyecto-list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.estudiante = self.request.user
        messages.success(self.request, 'Proyecto creado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo_pagina'] = 'Nuevo Proyecto'
        ctx['accion'] = 'Crear'
        return ctx
    
class ComentarioCreateView(LoginRequiredMixin, CreateView):
    model = Comentario
    form_class = ComentarioForm
    template_name = 'Ejercicio2App/comentario_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.proyecto = get_object_or_404(Proyecto, pk=self.kwargs['proyecto_pk'])
        if not self.proyecto.comentarios_activos():
            messages.warning(request, 'No se pueden agregar comentarios a un proyecto aprobado.')
            return redirect('proyecto-detail', pk=self.proyecto.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.proyecto = self.proyecto
        messages.success(self.request, 'Comentario publicado.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('proyecto-detail', kwargs={'pk': self.proyecto.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['proyecto'] = self.proyecto
        return ctx