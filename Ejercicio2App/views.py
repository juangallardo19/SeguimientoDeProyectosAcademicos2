from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import HttpResponseForbidden, HttpResponse

import csv
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from .models import Proyecto, Comentario
from .forms import ProyectoForm, DocenteProyectoForm, ComentarioForm


# ============================================================
# AUTENTICACIÓN
# ============================================================

def login_view(request):
    """
    Vista para iniciar sesión.
    Si el usuario ya está autenticado, lo manda al listado de proyectos.
    """

    if request.user.is_authenticated:
        return redirect('proyecto-list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, f'Bienvenido, {user.username}.')
            return redirect('proyecto-list')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'Ejercicio2App/login.html')


def logout_view(request):
    """
    Vista para cerrar sesión.
    """

    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('login')


# ============================================================
# HELPERS DE ROLES
# ============================================================

def es_docente(user):
    """
    Retorna True si el usuario pertenece al grupo docente
    o si es staff/superusuario.
    """

    return (
        user.is_authenticated
        and (
            user.groups.filter(name='docente').exists()
            or user.is_staff
            or user.is_superuser
        )
    )


def es_estudiante(user):
    """
    Retorna True si el usuario pertenece al grupo estudiante.
    """

    return (
        user.is_authenticated
        and user.groups.filter(name='estudiante').exists()
    )


# ============================================================
# PROYECTOS
# ============================================================

class ProyectoListView(LoginRequiredMixin, ListView):
    """
    Lista de proyectos.

    - El docente puede ver todos los proyectos.
    - El estudiante solo puede ver sus propios proyectos.
    - Permite filtrar por estado.
    - Si el usuario es docente, también puede filtrar por estudiante.
    """

    model = Proyecto
    template_name = 'Ejercicio2App/proyecto_list.html'
    context_object_name = 'proyectos'
    paginate_by = 10

    def get_queryset(self):
        qs = Proyecto.objects.select_related('estudiante')

        # Si NO es docente, solo ve sus proyectos
        if not es_docente(self.request.user):
            qs = qs.filter(estudiante=self.request.user)

        # Filtro por estado
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)

        # Filtro por estudiante, solo para docentes
        estudiante_id = self.request.GET.get('estudiante')
        if estudiante_id and es_docente(self.request.user):
            qs = qs.filter(estudiante__id=estudiante_id)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['es_docente'] = es_docente(self.request.user)
        ctx['estado_actual'] = self.request.GET.get('estado', '')
        ctx['estudiante_actual'] = self.request.GET.get('estudiante', '')
        ctx['total'] = self.get_queryset().count()

        # Lista de estudiantes para que el docente pueda filtrar
        ctx['estudiantes'] = User.objects.filter(
            groups__name='estudiante'
        ).distinct()

        return ctx


class ProyectoDetailView(LoginRequiredMixin, DetailView):
    """
    Detalle de un proyecto.

    - El docente puede ver cualquier proyecto.
    - El estudiante solo puede ver sus propios proyectos.
    - Carga comentarios.
    - Carga el formulario para que el docente actualice estado y calificación.
    """

    model = Proyecto
    template_name = 'Ejercicio2App/proyecto_detail.html'
    context_object_name = 'proyecto'

    def get_queryset(self):
        qs = Proyecto.objects.select_related('estudiante')

        # Si no es docente, solo puede entrar a sus propios proyectos
        if not es_docente(self.request.user):
            qs = qs.filter(estudiante=self.request.user)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['es_docente'] = es_docente(self.request.user)
        ctx['comentarios'] = self.object.comentarios.select_related('usuario')
        ctx['puede_comentar'] = self.object.comentarios_activos()
        ctx['docente_form'] = DocenteProyectoForm(instance=self.object)

        return ctx


class ProyectoCreateView(LoginRequiredMixin, CreateView):
    """
    Crear proyecto.

    - Solo los estudiantes pueden crear proyectos.
    - El estudiante se asigna automáticamente como dueño del proyecto.
    """

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


class ProyectoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Editar proyecto.

    - Solo el estudiante dueño del proyecto puede editarlo.
    - Los docentes no pueden editar por esta vista.
    """

    model = Proyecto
    form_class = ProyectoForm
    template_name = 'Ejercicio2App/proyecto_form.html'
    success_url = reverse_lazy('proyecto-list')

    def test_func(self):
        proyecto = self.get_object()

        return (
            proyecto.estudiante == self.request.user
            and not es_docente(self.request.user)
        )

    def form_valid(self, form):
        messages.success(self.request, 'Proyecto actualizado exitosamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['titulo_pagina'] = 'Editar Proyecto'
        ctx['accion'] = 'Guardar Cambios'

        return ctx


class ProyectoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Eliminar proyecto.

    - Solo el estudiante dueño del proyecto puede eliminarlo.
    - Los docentes no pueden eliminar por esta vista.
    """

    model = Proyecto
    template_name = 'Ejercicio2App/proyecto_confirm_delete.html'
    success_url = reverse_lazy('proyecto-list')

    def test_func(self):
        proyecto = self.get_object()

        return (
            proyecto.estudiante == self.request.user
            and not es_docente(self.request.user)
        )

    def form_valid(self, form):
        messages.success(self.request, 'Proyecto eliminado correctamente.')
        return super().form_valid(form)


@login_required
def docente_actualizar_proyecto(request, pk):
    """
    Vista exclusiva para docentes.

    Permite cambiar:
    - Estado
    - Calificación
    - Fecha de revisión
    """

    if not es_docente(request.user):
        return HttpResponseForbidden('No tienes permisos para realizar esta acción.')

    proyecto = get_object_or_404(Proyecto, pk=pk)

    if request.method == 'POST':
        form = DocenteProyectoForm(request.POST, instance=proyecto)

        if form.is_valid():
            proyecto = form.save(commit=False)

            if proyecto.estado in ['revision', 'aprobado']:
                proyecto.fecha_revision = timezone.now()

            proyecto.save()

            messages.success(
                request,
                f'Proyecto "{proyecto.titulo}" actualizado correctamente.'
            )

            return redirect('proyecto-detail', pk=pk)

        messages.error(request, 'Hay errores en el formulario.')

    return redirect('proyecto-detail', pk=pk)


# ============================================================
# COMENTARIOS
# ============================================================

class ComentarioCreateView(LoginRequiredMixin, CreateView):
    """
    Crear comentarios en un proyecto.

    - Los comentarios se bloquean si el proyecto está aprobado.
    - El usuario y el proyecto se asignan automáticamente.
    """

    model = Comentario
    form_class = ComentarioForm
    template_name = 'Ejercicio2App/comentario_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.proyecto = get_object_or_404(
            Proyecto,
            pk=self.kwargs['proyecto_pk']
        )

        # Si el usuario no es docente, solo puede comentar en sus proyectos
        if not es_docente(request.user) and self.proyecto.estudiante != request.user:
            messages.error(request, 'No tienes permiso para comentar este proyecto.')
            return redirect('proyecto-list')

        # Si el proyecto está aprobado, se bloquean los comentarios
        if not self.proyecto.comentarios_activos():
            messages.warning(
                request,
                'No se pueden agregar comentarios a un proyecto aprobado.'
            )
            return redirect('proyecto-detail', pk=self.proyecto.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.proyecto = self.proyecto

        messages.success(self.request, 'Comentario publicado correctamente.')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'proyecto-detail',
            kwargs={'pk': self.proyecto.pk}
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['proyecto'] = self.proyecto

        return ctx


# ============================================================
# EXPORTACIÓN CSV
# ============================================================

@login_required
def exportar_csv(request):
    """
    Exporta la lista de proyectos a CSV.

    - El docente exporta todos los proyectos.
    - El estudiante solo exporta sus propios proyectos.
    """

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="proyectos.csv"'

    # BOM para que Excel abra bien los caracteres especiales
    response.write('\ufeff')

    writer = csv.writer(response)

    writer.writerow([
        'ID',
        'Título',
        'Estudiante',
        'Estado',
        'Calificación',
        'Fecha de envío',
        'Fecha de revisión',
    ])

    qs = Proyecto.objects.select_related('estudiante')

    if not es_docente(request.user):
        qs = qs.filter(estudiante=request.user)

    # Mantener filtros si vienen desde la URL
    estado = request.GET.get('estado')
    if estado:
        qs = qs.filter(estado=estado)

    estudiante_id = request.GET.get('estudiante')
    if estudiante_id and es_docente(request.user):
        qs = qs.filter(estudiante__id=estudiante_id)

    for proyecto in qs:
        writer.writerow([
            proyecto.pk,
            proyecto.titulo,
            proyecto.estudiante.get_full_name() or proyecto.estudiante.username,
            proyecto.get_estado_display(),
            proyecto.calificacion or '',
            proyecto.fecha_envio.strftime('%Y-%m-%d %H:%M'),
            proyecto.fecha_revision.strftime('%Y-%m-%d %H:%M') if proyecto.fecha_revision else '',
        ])

    return response


# ============================================================
# EXPORTACIÓN PDF
# ============================================================

@login_required
def exportar_pdf(request):
    """
    Exporta la lista de proyectos a PDF.

    - El docente exporta todos los proyectos.
    - El estudiante solo exporta sus propios proyectos.
    """

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    titulo = Paragraph('Reporte de Proyectos Académicos', styles['Title'])
    usuario = Paragraph(
        f'Generado por: {request.user.username}',
        styles['Normal']
    )

    elements.append(titulo)
    elements.append(usuario)

    data = [
        [
            'ID',
            'Título',
            'Estudiante',
            'Estado',
            'Calificación',
        ]
    ]

    qs = Proyecto.objects.select_related('estudiante')

    if not es_docente(request.user):
        qs = qs.filter(estudiante=request.user)

    # Mantener filtros si vienen desde la URL
    estado = request.GET.get('estado')
    if estado:
        qs = qs.filter(estado=estado)

    estudiante_id = request.GET.get('estudiante')
    if estudiante_id and es_docente(request.user):
        qs = qs.filter(estudiante__id=estudiante_id)

    for proyecto in qs:
        data.append([
            str(proyecto.pk),
            proyecto.titulo[:40],
            proyecto.estudiante.username,
            proyecto.get_estado_display(),
            str(proyecto.calificacion or '—'),
        ])

    tabla = Table(
        data,
        colWidths=[40, 200, 100, 90, 80]
    )

    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),

        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
            colors.whitesmoke,
            colors.white,
        ]),

        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(tabla)

    doc.build(elements)

    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="proyectos.pdf"'

    return response