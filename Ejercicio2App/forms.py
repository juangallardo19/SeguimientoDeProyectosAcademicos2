from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from .models import Proyecto, Comentario



class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['titulo', 'descripcion', 'documento']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'titulo': 'Título del proyecto',
            'descripcion': 'Descripción',
            'documento': 'Documento PDF opcional',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Field('titulo', css_class='form-group'),
            Field('descripcion', css_class='form-group'),
            Field('documento', css_class='form-group'),
        )

    def get_queryset(self):
        qs = Proyecto.objects.select_related('estudiante')

        if not es_docente(self.request.user):
            qs = qs.filter(estudiante=self.request.user)

        estado = self.request.GET.get('estado')
        estudiante_id = self.request.GET.get('estudiante')

        if estado:
            qs = qs.filter(estado=estado)

        if estudiante_id and es_docente(self.request.user):
            qs = qs.filter(estudiante__id=estudiante_id)

        return qs

class DocenteProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['estado', 'calificacion']
        labels = {
            'estado': 'Estado del proyecto',
            'calificacion': 'Calificación',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Escribe tu comentario aquí...'
            }),
        }
        labels = {
            'texto': 'Comentario',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('texto'),
            Submit('submit', 'Publicar comentario', css_class='btn btn-primary'),
        )