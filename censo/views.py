from django.urls import reverse_lazy, reverse
from typing import Any
from django import http
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect,get_object_or_404
from django.views.generic import ListView, CreateView, View, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .models import *
from datetime import date,timedelta
from django.http import JsonResponse
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.contrib import messages
from .utils import render_to_pdf
from django.template.loader import get_template
from weasyprint import HTML, CSS
from proyecto import wsgi
from proyecto import settings
import os







today = date.today()
def funcionEdad(habitantes):
    for habitante in habitantes:
        age = today.year - habitante.fecha_nacimiento.year - ((today.month, today.day) < (habitante.fecha_nacimiento.month, habitante.fecha_nacimiento.day))
        habitante.edad = age
def funcionEdad1(habitantes):
    for habitante in habitantes:
        age = today.year - habitante.Habitante.fecha_nacimiento.year - ((today.month, today.day) < (habitante.Habitante.fecha_nacimiento.month, habitante.Habitante.fecha_nacimiento.day))
        habitante.Habitante.edad = age



def registrar_usuario(request):
    if request.method == 'GET':
        return render(request, 'login/registrar.html')
    elif request.method == 'POST':
        usuario = request.POST.get('usuario')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not usuario or not password1 or not password2:
            error = "Por favor rellene todos los campos"
            return render(request, 'login/registrar.html', {'error': error})

        if password1 != password2:
            error = "Las contraseñas no coinciden"
            return render(request, 'login/registrar.html', {'error': error})

        try:
            user = User.objects.create_user(
                username=usuario,
                password=password1
            )
            user.save()
            login(request, user)
            return redirect('inicio')
        except IntegrityError:
            error = f"El usuario {usuario} ya existe"
            return render(request, 'login/registrar.html', {'error': error})
        
        

def iniciar_sesion(request):
    if request.method == 'GET':
        return render(request, 'login/ingresar.html')

    else:
        print(request.POST)

        user = authenticate(
            request,
            username=request.POST["usuario"],
            password=request.POST["password"],
        )
        
        if user is None:

            error='Usuario o contraseña incorrecta'
            return render(request,'login/ingresar.html', {'error': error } )
        else:
            login(request,user)

            return redirect('inicio')
@login_required
def inicio(request):
    # Contar todos los habitantes
    cantidad_habitantes = Habitante.objects.all().count()

    # Contar todos los jefes de familia
    cantidad_jefes = JefeFamiliar.objects.all().count()

    # Contar todas las cargas familiares
    cantidad_cargas = CargaFamiliar.objects.all().count()

    # Calcular la fecha actual y las fechas límite para niños, ancianos y discapacitados
    today = date.today()
    fecha_ninos = today - timedelta(days=12 * 365.25)
    fecha_ancianos = today - timedelta(days=65 * 365.25)

    # Contar niños
    cantidad_ninos = Habitante.objects.filter(fecha_nacimiento__gte=fecha_ninos).count()

    # Contar ancianos
    cantidad_ancianos = Habitante.objects.filter(fecha_nacimiento__lte=fecha_ancianos).count()

    # Contar discapacitados
    cantidad_discapacitados = Habitante.objects.filter(discapacidad='Sí').count()

    return render(request, 'principal.html', {
        'cantidad_habitantes': cantidad_habitantes,
        'cantidad_jefes_familia': cantidad_jefes,
        'cantidad_cargas_familiares': cantidad_cargas,
        'cantidad_niños': cantidad_ninos,
        'cantidad_ancianos': cantidad_ancianos,
        'cantidad_discapacitados': cantidad_discapacitados,
    })


from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def configurar_usuario(request):
    if request.method == 'POST':
        # Actualizar nombre de usuario
        nuevo_nombre_usuario = request.POST.get('nuevo_nombre_usuario')
        if nuevo_nombre_usuario:
            request.user.username = nuevo_nombre_usuario
            request.user.save()

        # Cambiar contraseña
        nueva_contraseña = request.POST.get('new_password1')
        if nueva_contraseña:
            request.user.set_password(nueva_contraseña)
            request.user.save()

        # Iniciar sesión con el nuevo nombre de usuario y contraseña
        user = authenticate(
            request,
            username=nuevo_nombre_usuario,
            password=nueva_contraseña,
        )
        if user:
            login(request, user)
            return redirect('inicio')

    return render(request, 'login/configurar.html')

class habitantes(LoginRequiredMixin,ListView):
    model = Habitante
    template_name = 'habitantes/habitantes.html'
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            data = Habitante.objects.get(pk=request.POST['id']).toJSON()
        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Lista Habitantes'
        context['crear_habitante'] = reverse_lazy('crear_habitantes')
        context['seccion'] = 'Habitantes'
        habitantes = context['object_list']
        funcionEdad(habitantes)
        return context
    

class crear_habitantes(LoginRequiredMixin,CreateView):
    model=Habitante
    form_class = HabitanteForm
    template_name = 'habitantes/crear_habitante.html'
    success_url = reverse_lazy('habitantes')

    # def post(self, request, *args, **kwargs):
    #     form = HabitanteForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    #         return HttpResponseRedirect(self.success_url)
    #     self.object = None
    #     context = self.get_context_data(**kwargs)
    #     context['form']:form
    #     return render(request, self.template_name,context)
        

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar Habitante'
        context['seccion'] = 'Registrar Habitante'
        context['boton'] = 'Registrar habitante'
        return context

class editar_habitantes(UpdateView):
    model=Habitante
    form_class = HabitanteForm
    template_name = 'habitantes/crear_habitante.html'
    success_url = reverse_lazy('habitantes')
    

    def get(self, request, *args, **kwargs):
        habitante = get_object_or_404(Habitante, pk=self.kwargs.get('pk'))
        formatted_birthdate = habitante.fecha_nacimiento.strftime('%Y-%m-%d')
        form = self.form_class(instance=habitante, initial={'fecha_nacimiento': formatted_birthdate})
        return render(request, self.template_name, {'form': form, 'titulo':'Editar Habitante',
                                                    'seccion': 'Editar Habitante',
                                                    'boton':'Actualizar Habitante'})
        
    #No funciona, ya que estoy reescribiendo todo en el metodo de arriba
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Habitante'
        context['seccion'] = 'Editar Habitante'
        context['boton'] = 'Actualizar habitante'
        return context


def jefe_familiar(request):
     data = {
         'jefes': JefeFamiliar.objects.all()
     }
     return render(request, 'jefe.html', data)

class EliminarHabitante(DeleteView):

    model = Habitante
    template_name = 'habitantes/eliminar_habitante.html'  # Crea este template en tu carpeta 'templates/jefes/'
    success_url = reverse_lazy('habitantes')  # Reemplaza 'habitantes' con la URL a la que deseas redirigir después de eliminar el jefe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Habitante'
        context['seccion'] = 'Eliminar Habitante'
        context['boton'] = 'Eliminar Habitante'
        return context

class JefeFamiliarCrear(LoginRequiredMixin, CreateView):
    template_name = 'jefes/crear_jefe.html'
    form_class = HabitanteForm
    second_form_class = JefeForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        form2 = self.second_form_class()
        return render(request, self.template_name, {'form': form, 'form2': form2,
                                                    'boton': 'Registrar jefe familiar', 'seccion': 'Registrar Jefe',
                                                    'titulo': 'Registrar Jefe Familiar'})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        form2 = self.second_form_class(request.POST)
        if form.is_valid() and form2.is_valid():
            cedula = form.cleaned_data['cedula']
            if cedula == None:
                messages.error(request, 'El jefe familiar no puede ser registrado sin cedula')
                return render(request, self.template_name, {'form': form, 'form2': form2,
                                                    'boton': 'Registrar jefe familiar', 'seccion': 'Registrar Jefe',
                                                    'titulo': 'Registrar Jefe Familiar'})
            fecha_limite = date(2005, 11, 25)
            fecha_nacimiento = form.cleaned_data['fecha_nacimiento']

            if fecha_nacimiento > fecha_limite:
                messages.error(request, 'El jefe familiar no puede ser un niño.')
                return render(request, self.template_name, {'form': form, 'form2': form2,
                                                    'boton': 'Registrar jefe familiar', 'seccion': 'Registrar Jefe',
                                                    'titulo': 'Registrar Jefe Familiar'})
            habitante = form.save()
            vivienda = request.POST.get('tipo_casa')
            direccion_jefe = request.POST.get('direccion')
            numero_casa = int(request.POST.get('numeroCasa'))
            numero_calle = int(request.POST.get('numeroCalle'))
            jefe_familiar = JefeFamiliar(Habitante=habitante, tipo_casa=vivienda, numeroCasa = numero_casa,
            numeroCalle = numero_calle, direccion=direccion_jefe)
            jefe_familiar.save()
            return redirect('jefes_familia')
        else:
            print(form.errors, form2.errors)

        return render(request, self.template_name, {'form': form, 'form2': form2,
                                                    'boton': 'Registrar jefe familiar', 'seccion': 'Registrar Jefe',
                                                    'titulo': 'Registrar Jefe Familiar'})


        
class JefeFamiliarEditar(UpdateView):


    model = JefeFamiliar
    template_name = 'jefes/ver_jefe.html'
    form_class = HabitanteForm
    second_form_class = JefeForm
    pk_url_kwarg = 'jefe_id'

    def get(self, request, *args, **kwargs):
        jefe = get_object_or_404(JefeFamiliar, pk=self.kwargs.get('jefe_id'))
        formatted_birthdate = jefe.Habitante.fecha_nacimiento.strftime('%Y-%m-%d')
        form = self.form_class(instance=jefe.Habitante, initial={'fecha_nacimiento': formatted_birthdate})
        form2 = self.second_form_class(instance=jefe)
        cargas_familiares = CargaFamiliar.objects.filter(jefe_familiar=jefe)
        funcionEdad1(cargas_familiares)
    
        return render(request, self.template_name, {'form': form, 'form2': form2,
                                                    'boton': 'Actualizar jefe familiar', 'seccion': 'Editar Jefe',
                                                    'titulo': 'Editar Jefe Familiar','cargas':cargas_familiares})

    def post(self, request, *args, **kwargs):
        jefe = get_object_or_404(JefeFamiliar, pk=self.kwargs.get('jefe_id'))
        form = self.form_class(request.POST, instance=jefe.Habitante)
        form2 = self.second_form_class(request.POST, instance=jefe)
        if form.is_valid() and form2.is_valid():
            cedula = form.cleaned_data['cedula']
            if cedula == None:
                messages.error(request, 'El jefe familiar no puede ser guardado sin cedula')
                return render(request, self.template_name, {'form': form, 'form2': form2,
                                                    'boton': 'Registrar jefe familiar', 'seccion': 'Registrar Jefe',
                                                    'titulo': 'Registrar Jefe Familiar'})
            fecha_limite = date(2005, 11, 25)
            fecha_nacimiento = form.cleaned_data['fecha_nacimiento']

            if fecha_nacimiento > fecha_limite:
                messages.error(request, 'El jefe familiar no puede ser un niño.')
                return render(request, self.template_name, {'form': form, 'form2': form2,
                                                    'boton': 'Registrar jefe familiar', 'seccion': 'Registrar Jefe',
                                                    'titulo': 'Registrar Jefe Familiar'})
            habitante = form.save()
            vivienda = request.POST.get('tipo_casa')
            jefe.Habitante = habitante
            jefe.tipo_casa = vivienda
            jefe.save()
            return redirect('jefes_familia')
        else:
            print(form.errors)
        return render(request, self.template_name, {'form': form, 'form2': form2,
                                                    'boton': 'Actualizar jefe familiar', 'seccion': 'Editar Jefe',
                                                    'titulo': 'Editar Jefe Familiar'})

class EliminarJefeFamiliar(DeleteView):

    model = Habitante
    template_name = 'jefes/eliminar_jefe.html'  # Crea este template en tu carpeta 'templates/jefes/'
    success_url = reverse_lazy('jefes_familia')  # Reemplaza 'habitantes' con la URL a la que deseas redirigir después de eliminar el jefe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Jefe Familiar'
        context['seccion'] = 'Eliminar Jefe'
        context['boton'] = 'Eliminar Jefe Familiar'
        return context

class CargasJefe(ListView):
    template_name = 'jefes/cargas_jefe.html'
    model = JefeFamiliar
    pk_url_kwarg = 'jefe_id'

    def get(self, request, *args, **kwargs):
        jefe = get_object_or_404(JefeFamiliar, pk=self.kwargs.get('jefe_id'))
        cargas_familiares = CargaFamiliar.objects.filter(jefe_familiar=jefe)
        funcionEdad1(cargas_familiares)
    
        return render(request, self.template_name, {'boton': 'Actualizar jefe familiar', 'seccion': 'Editar Jefe',
                                                    'titulo': f'Carga Familiar de {jefe.Habitante.nombre} {jefe.Habitante.apellido} C.I: {jefe.Habitante.cedula}',
                                                    'cargas':cargas_familiares})


    
 

class CargaFamiliarCrear(LoginRequiredMixin,View):
    template_name = 'cargas/crear_carga.html'
    form_class = {'form1':HabitanteForm,
                  'form2':CargaForm}

    def get(self, request):
        form = self.form_class['form1']()
        form2 = self.form_class['form2']()
        return render(request, self.template_name, {'form':form, 'form2':form2,
                                                    'boton':'Registrar carga familiar', 'seccion':'Registrar carga',
                                                    'titulo':'Registrar carga Familiar'})
    
    def post(self, request):
        form = self.form_class['form1'](request.POST)
        form2 = self.form_class['form2'](request.POST)


        if form.is_valid():
            habitante = form.save()

            jefe_familiar_id = request.POST['jefe_familiar']  # Asume que obtienes el ID del jefe familiar del formulario
            jefe_familiar = JefeFamiliar.objects.get(pk=jefe_familiar_id)
            carga_familiar = CargaFamiliar(Habitante=habitante, jefe_familiar=jefe_familiar)
            carga_familiar.save()

            return redirect('carga_familiar')  # Reemplaza 'carga_familiar_list' con la URL de tu lista de cargas familiares
        return render(request, self.template_name, {'form':form, 'form2':form2,
                                                    'boton':'Registrar carga familiar', 'seccion':'Registrar carga',
                                                    'titulo':'Registrar carga Familiar'})

class EliminarCargaFamiliar(DeleteView):

    model = Habitante
    template_name = 'cargas/eliminar_carga.html'  # Crea este template en tu carpeta 'templates/jefes/'
    success_url = reverse_lazy('carga_familiar')  # Reemplaza 'habitantes' con la URL a la que deseas redirigir después de eliminar el jefe

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar Carga Familiar'
        context['seccion'] = 'Eliminar Carga'
        context['boton'] = 'Eliminar Carga Familiar'
        return context

class CargaFamiliarList(LoginRequiredMixin,ListView):
    model = CargaFamiliar
    template_name = 'cargas/cargas_familiares.html'

    def post(self, request, *args, **kwargs):
        data={}
        #print(request.POST)
        try:
            data = CargaFamiliar.objects.get(pk=request.POST['id']).toJSON()

            #hab = Habitante.objects.get(pk=request.POST['id'])
            #data['nombre'] = hab.nombre
        except Exception as e:
            #data['error'] = 'No se encontro el habitante con el id '+str(request.POST['id'])
            data['error'] = str(e)
  

        return JsonResponse(data)
    
    def get_context_data(self, **kwargs):

        context=super().get_context_data(**kwargs)
        context['titulo'] = 'Lista Cargas Familiares'
        context['crear_habitante'] = reverse_lazy('crear_carga')
        context['seccion'] = 'Lista Cargas Familiares'
        cargas = context['object_list']
        funcionEdad1(cargas)
        return context
    
class CargaFamiliarEditar(UpdateView):
    model = CargaFamiliar
    template_name = 'cargas/crear_carga.html'
    form_class = HabitanteForm
    second_form_class = CargaForm
    pk_url_kwarg = 'carga_id'

    def get(self, request, *args, **kwargs):
        carga = get_object_or_404(CargaFamiliar, pk=self.kwargs.get('carga_id'))
        formatted_birthdate = carga.Habitante.fecha_nacimiento.strftime('%Y-%m-%d')
        form = self.form_class(instance=carga.Habitante, initial={'fecha_nacimiento': formatted_birthdate})
        form2 = self.second_form_class(instance=carga)
        return render(request, self.template_name, {'form': form, 'form2': form2,
                                                    'boton': 'Actualizar Carga familiar', 'seccion': 'Editar Carga',
                                                    'titulo': 'Editar Carga Familiar'})

    def post(self, request, *args, **kwargs):
        carga = get_object_or_404(CargaFamiliar, pk=self.kwargs.get('carga_id'))
        form = self.form_class(request.POST, instance=carga.Habitante)
        form2 = self.second_form_class(request.POST, instance=carga)
        if form.is_valid() and form2.is_valid():
            habitante = form.save()
            jefe_familiar_id = request.POST['jefe_familiar']
            
            carga.Habitante = habitante
            jefeFamiliar = JefeFamiliar.objects.get(pk=jefe_familiar_id)
            carga.jefe_familiar = jefeFamiliar
            carga.save()
            return redirect('carga_familiar')
        else:
            print(form.errors)
        return render(request, self.template_name, {'form': form, 'form2': form2,
                                                    'boton': 'Actualizar jefe familiar', 'seccion': 'Editar Jefe',
                                                    'titulo': 'Editar Jefe Familiar'})



class JefeFamiliarList(LoginRequiredMixin,ListView):
    model = JefeFamiliar
    template_name = 'jefes/jefes_familiares.html'
    
    def post(self, request, *args, **kwargs):
        data = {}
        
        try:
            data['jefe_familiar'] = JefeFamiliar.objects.get(pk=request.POST['id']).toJSON()

        except Exception as e:
            data['error'] = str(e)

        return JsonResponse(data)

    def get_context_data(self, **kwargs):

        context=super().get_context_data(**kwargs)
        context['titulo'] = 'Lista Jefes Familiares'
        context['crear_habitante'] = reverse_lazy('crear_jefe')
        context['seccion'] = 'Lista Jefes'
        jefes = context['object_list']
        funcionEdad1(jefes)
        return context
    
class MostrarNiños(View):
    template_name = 'habitantes/mostrar_niños.html'

    def get(self, request):
        fecha_actual = date.today()
        fecha_12_anios_atras = fecha_actual - timedelta(days=12 * 365.25)
        habitantes_niños = CargaFamiliar.objects.filter(Habitante__fecha_nacimiento__gte=fecha_12_anios_atras)
        funcionEdad1(habitantes_niños)
        return render(request, self.template_name, {'habitantes_niños': habitantes_niños, 'titulo':'Lista de niños',
                                                    'seccion':'Niños'})
    
class MostrarAncianos(View):
    template_name = 'habitantes/mostrar_ancianos.html'

    def get(self, request):
        fecha_actual = date.today()
        fecha_65_anios_atras = fecha_actual - timedelta(days=65 * 365.25)

        # Filtrar ancianos que son Jefes Familiares
        jefes_ancianos = JefeFamiliar.objects.filter(Habitante__fecha_nacimiento__lte=fecha_65_anios_atras)

        # Filtrar ancianos que son Cargas Familiares
        cargas_ancianos = CargaFamiliar.objects.filter(Habitante__fecha_nacimiento__lte=fecha_65_anios_atras)
        funcionEdad1(jefes_ancianos)
        funcionEdad1(cargas_ancianos)
        # Combinar las dos listas de ancianos
        ancianos = [
            {'Habitante': anciano.Habitante, 'jefe_familiar': True} for anciano in jefes_ancianos
        ] + [
            {'Habitante': anciano.Habitante, 'jefe_familiar': False} for anciano in cargas_ancianos
        ]

        return render(request, self.template_name, {'ancianos': ancianos, 'titulo': 'Lista de Ancianos',
 
                                                    'seccion':'Ancianos'})
    
class HabitantesListView(LoginRequiredMixin,View):
    template_name = 'habitantes/habitantes.html'

    def get(self, request):

        jefes_habitantes = JefeFamiliar.objects.all()

        # Filtrar habitantes que son Cargas Familiares
        cargas_habitantes = CargaFamiliar.objects.all()
        funcionEdad1(jefes_habitantes)
        funcionEdad1(cargas_habitantes)
        # Combinar las dos listas de habitantes
        habitantes = [
            {'Habitante': habitante.Habitante, 'jefe_familiar': True} for habitante in jefes_habitantes
        ] + [
            {'Habitante': habitante.Habitante, 'jefe_familiar': False} for habitante in cargas_habitantes
        ]

        return render(request, self.template_name, {'habitantes': habitantes, 'titulo': 'Lista de habitantes',
 
                                                    'seccion':'habitantes'})

class MostrarDiscapacitados(View):
    template_name = 'habitantes/mostrar_discapacitados.html'

    def get(self, request):
        jefes_discapacitados = JefeFamiliar.objects.filter(Habitante__discapacidad='Sí')
        cargas_discapacitados = CargaFamiliar.objects.filter(Habitante__discapacidad='Sí')
        funcionEdad1(jefes_discapacitados)
        funcionEdad1(cargas_discapacitados)
        discapacitados = [
            {'Habitante': habitante.Habitante, 'jefe_familiar': True} for habitante in jefes_discapacitados
        ] + [
            {'Habitante': habitante.Habitante, 'jefe_familiar': False} for habitante in cargas_discapacitados
        ]
        
        return render(request, self.template_name, {'discapacitados': discapacitados, 'titulo': 'Lista de discapacitados',
 
                                                    'seccion':'discapacitados'})

class MostrarMujeres(View):
    template_name = 'habitantes/mostrar_mujeres.html'

    def get(self, request):
        jefes_mujeres = JefeFamiliar.objects.filter(Habitante__genero='Femenino')
        cargas_mujeres = CargaFamiliar.objects.filter(Habitante__genero='Femenino')
        funcionEdad1(jefes_mujeres)
        funcionEdad1(cargas_mujeres)
        mujeres = [
            {'Habitante': habitante.Habitante, 'jefe_familiar': True} for habitante in jefes_mujeres
        ] + [
            {'Habitante': habitante.Habitante, 'jefe_familiar': False} for habitante in cargas_mujeres
        ]
        return render(request, self.template_name, {'mujeres': mujeres, 'titulo': 'Lista de mujeres',
 
                                                    'seccion':'mujeres'})
class MostrarEmbarazadas(View):
    template_name = 'habitantes/mostrar_embarazadas.html'

    def get(self, request):
        jefes_embarazadas = JefeFamiliar.objects.filter(Habitante__mujer_embarazada='Sí')
        cargas_embarazadas = CargaFamiliar.objects.filter(Habitante__mujer_embarazada='Sí')
        funcionEdad1(jefes_embarazadas)
        funcionEdad1(cargas_embarazadas)
        embarazadas = [
            {'Habitante': habitante.Habitante, 'jefe_familiar': True} for habitante in jefes_embarazadas
        ] + [
            {'Habitante': habitante.Habitante, 'jefe_familiar': False} for habitante in cargas_embarazadas
        ]
        return render(request, self.template_name, {'embarazadas': embarazadas, 'titulo': 'Lista de embarazadas',
 
                                                    'seccion':'embarazadas'})
    
class MostrarHombres(View):
    template_name = 'habitantes/mostrar_hombres.html'

    def get(self, request):
        jefes_hombres = JefeFamiliar.objects.filter(Habitante__genero='Masculino')
        cargas_hombres = CargaFamiliar.objects.filter(Habitante__genero='Masculino')
        funcionEdad1(jefes_hombres)
        funcionEdad1(cargas_hombres)
        hombres = [
            {'Habitante': habitante.Habitante, 'jefe_familiar': True} for habitante in jefes_hombres
        ] + [
            {'Habitante': habitante.Habitante, 'jefe_familiar': False} for habitante in cargas_hombres
        ]
        return render(request, self.template_name, {'hombres': hombres, 'titulo': 'Lista de hombres',
 
                                                    'seccion':'hombres'})
class MostrarVotante(View):
    template_name = 'habitantes/mostrar_votantes.html'

    def get(self, request):
        jefes_votantes = JefeFamiliar.objects.filter(Habitante__vota='Sí')
        cargas_votantes = CargaFamiliar.objects.filter(Habitante__vota='Sí')
        funcionEdad1(jefes_votantes)
        funcionEdad1(cargas_votantes)
        votantes = [
            {'Habitante': habitante.Habitante, 'jefe_familiar': True} for habitante in jefes_votantes
        ] + [
            {'Habitante': habitante.Habitante, 'jefe_familiar': False} for habitante in cargas_votantes
        ]
        return render(request, self.template_name, {'votantes': votantes, 'titulo': 'Lista de votantes',
 
                                                    'seccion':'votantes'})
    
class MostrarVivientes(ListView):

    model = JefeFamiliar
    template_name = 'habitantes/mostrar_vivientes.html'

    def get_context_data(self, **kwargs):

        context=super().get_context_data(**kwargs)
        context['titulo'] = 'Lista por Casa'
        context['crear_habitante'] = reverse_lazy('crear_jefe')
        context['seccion'] = 'Lista Por Casas'
        jefes = context['object_list']
        funcionEdad1(jefes)
        return context
    
##################### PDF ###################

class HabitantesPDF(View):
    template_name = 'pdf/habitantes.html'

    def get(self, request, *args, **kwargs):
        
        habitantes = Habitante.objects.all()
        data = { 
            'total_habitantes': habitantes.count(),
            'habitantes': habitantes
        }
        pdf = render_to_pdf(self.template_name, data)
        return HttpResponse(pdf, content_type = "application/pdf")


def HabitantesPDF(request):
  # Obtenemos la plantilla HTML
  fecha=date.today()
  template = get_template('pdf/prueba.html')
  habitantes = Habitante.objects.all()
  funcionEdad(habitantes)
  context =  { 
            'total_habitantes': habitantes.count(),
            'habitantes': habitantes,
            'fecha':fecha
        }
  css_url = os.path.join(settings.BASE_DIR, 'proyecto/static/lib/bootstrap-4.6.2-dist/css/bootstrap.min.css')
  print('Direccion:',css_url)
  pdf = HTML(string=template.render(context), base_url=request.build_absolute_uri()).write_pdf()

  # Devolvemos el PDF como respuesta
  return HttpResponse(pdf, content_type='application/pdf')

class JefePDF(View):

    def get(self, request, *args, **kwargs):
        try:
            template = get_template('pdf/jefe.html')
            jefe = JefeFamiliar.objects.get(pk=self.kwargs['pk'])
            cargas_familiares = CargaFamiliar.objects.filter(jefe_familiar=jefe)
            funcionEdad1(cargas_familiares)
            context = {
                'jefe': jefe,
                'cargas': cargas_familiares,
                'cantidad':cargas_familiares.count(),
                'fecha':date.today()
            }
            html = template.render(context)
            css_url = os.path.join(settings.BASE_DIR, 'proyecto/static/lib/bootstrap-4.6.2-dist/css/bootstrap.min.css')
            pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
            return HttpResponse(pdf, content_type='application/pdf')
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('inicio'))

def JefesPDF(request):
    fecha = date.today()
    template = get_template('pdf/jefes.html')
    jefes = JefeFamiliar.objects.all()
    cargas_familiares = CargaFamiliar.objects.all()
    funcionEdad1(jefes)
    context = {
        'total_jefes': jefes.count(),
        'jefes': jefes,
        'cargas': cargas_familiares,
        'cantidad': cargas_familiares.count(),
        'fecha': date.today()
    }
    html = template.render(context)
    css_url = os.path.join(settings.BASE_DIR, 'proyecto/static/lib/bootstrap-4.6.2-dist/css/bootstrap.min.css')
    pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    return HttpResponse(pdf, content_type='application/pdf')

def CargasPDF(request):
  # Obtenemos la plantilla HTML
    fecha=date.today()
    template = get_template('pdf/cargas.html')
    cargas = CargaFamiliar.objects.all()
    funcionEdad1(cargas)
    context =  { 
            'total_cargas': cargas.count(),
            'cargas': cargas,
            'fecha':fecha
        }
    css_url = os.path.join(settings.BASE_DIR, 'proyecto/static/lib/bootstrap-4.6.2-dist/css/bootstrap.min.css')
    print('Direccion:',css_url)
    pdf = HTML(string=template.render(context), base_url=request.build_absolute_uri()).write_pdf()

    # Devolvemos el PDF como respuesta
    return HttpResponse(pdf, content_type='application/pdf')


def NiñosPDF(request):

    fecha_actual = date.today()
    template = get_template('pdf/niños.html')
    fecha_12_anios_atras = fecha_actual - timedelta(days=12 * 365.25)
    niños = CargaFamiliar.objects.filter(Habitante__fecha_nacimiento__gte=fecha_12_anios_atras)
    funcionEdad1(niños)
    context =  { 
                'total_niños': niños.count(),
                'niños': niños,
                'fecha':fecha_actual
            }
    css_url = os.path.join(settings.BASE_DIR, 'proyecto/static/lib/bootstrap-4.6.2-dist/css/bootstrap.min.css')
    print('Direccion:',css_url)
    pdf = HTML(string=template.render(context), base_url=request.build_absolute_uri()).write_pdf()

    # Devolvemos el PDF como respuesta
    return HttpResponse(pdf, content_type='application/pdf')

def AncianosPDF(request):

    fecha_actual = date.today()
    template = get_template('pdf/ancianos.html')
    fecha_65_anios_atras = fecha_actual - timedelta(days=65 * 365.25)
    ancianos= Habitante.objects.filter(fecha_nacimiento__lte=fecha_65_anios_atras)
    funcionEdad(ancianos)
    context =  { 
                'total_ancianos': ancianos.count(),
                'ancianos': ancianos,
                'fecha':fecha_actual
            }
    css_url = os.path.join(settings.BASE_DIR, 'proyecto/static/lib/bootstrap-4.6.2-dist/css/bootstrap.min.css')
    print('Direccion:',css_url)
    pdf = HTML(string=template.render(context), base_url=request.build_absolute_uri()).write_pdf()

    # Devolvemos el PDF como respuesta
    return HttpResponse(pdf, content_type='application/pdf')

def DiscapacitadosPDF(request):

    fecha_actual = date.today()
    template = get_template('pdf/discapacitados.html')
    
    discapacitados= Habitante.objects.filter(discapacidad='Sí')
    funcionEdad(discapacitados)
    context =  { 
                'total_discapacitados': discapacitados.count(),
                'discapacitados': discapacitados,
                'fecha':fecha_actual
            }
    css_url = os.path.join(settings.BASE_DIR, 'proyecto/static/lib/bootstrap-4.6.2-dist/css/bootstrap.min.css')
    print('Direccion:',css_url)
    pdf = HTML(string=template.render(context), base_url=request.build_absolute_uri()).write_pdf()

    # Devolvemos el PDF como respuesta
    return HttpResponse(pdf, content_type='application/pdf')

def HombresPDF(request):

    fecha_actual = date.today()
    template = get_template('pdf/hombres.html')
    
    hombres= Habitante.objects.filter(genero='Masculino')
    funcionEdad(hombres)
    context =  { 
                'total_hombres': hombres.count(),
                'hombres': hombres,
                'fecha':fecha_actual
            }
    css_url = os.path.join(settings.BASE_DIR, 'proyecto/static/lib/bootstrap-4.6.2-dist/css/bootstrap.min.css')
    print('Direccion:',css_url)
    pdf = HTML(string=template.render(context), base_url=request.build_absolute_uri()).write_pdf()

    # Devolvemos el PDF como respuesta
    return HttpResponse(pdf, content_type='application/pdf')

def MujeresPDF(request):

    fecha_actual = date.today()
    template = get_template('pdf/mujeres.html')

    mujeres = Habitante.objects.filter(genero='Femenino')
    funcionEdad(mujeres)
    context =  { 
                'total_mujeres': mujeres.count(),
                'mujeres': mujeres,
                'fecha':fecha_actual
            }
    css_url = os.path.join(settings.BASE_DIR, 'proyecto/static/lib/bootstrap-4.6.2-dist/css/bootstrap.min.css')
    print('Direccion:',css_url)
    pdf = HTML(string=template.render(context), base_url=request.build_absolute_uri()).write_pdf() 

    # Devolvemos el PDF como respuesta
    return HttpResponse(pdf, content_type='application/pdf')

def EmbarazadasPDF(request):

    fecha_actual = date.today()
    template = get_template('pdf/embarazadas.html')

    embarazadas = Habitante.objects.filter(genero='Femenino')
    funcionEdad(embarazadas)
    context =  { 
                'total_embarazadas': embarazadas.count(),
                'embarazadas': embarazadas,
                'fecha':fecha_actual
            }
    css_url = os.path.join(settings.BASE_DIR, 'proyecto/static/lib/bootstrap-4.6.2-dist/css/bootstrap.min.css')
    print('Direccion:',css_url)
    pdf = HTML(string=template.render(context), base_url=request.build_absolute_uri()).write_pdf() 

    # Devolvemos el PDF como respuesta
    return HttpResponse(pdf, content_type='application/pdf')

def VotantesPDF(request):

    fecha_actual = date.today()
    template = get_template('pdf/votantes.html')

    votantes = Habitante.objects.filter(vota='Sí')
    funcionEdad(votantes)
    context =  { 
                'total_votantes': votantes.count(),
                'votantes': votantes,
                'fecha':fecha_actual
            }
    css_url = os.path.join(settings.BASE_DIR, 'proyecto/static/lib/bootstrap-4.6.2-dist/css/bootstrap.min.css')
    print('Direccion:',css_url)
    pdf = HTML(string=template.render(context), base_url=request.build_absolute_uri()).write_pdf() 

    # Devolvemos el PDF como respuesta
    return HttpResponse(pdf, content_type='application/pdf')

def ViviendasPDF(request):
    fecha = date.today()
    template = get_template('pdf/casas.html')
    jefes = JefeFamiliar.objects.all()
    cargas_familiares = CargaFamiliar.objects.all()
    funcionEdad1(jefes)
    context = {
        'total_jefes': jefes.count(),
        'jefes': jefes,
        'cargas': cargas_familiares,
        'cantidad': cargas_familiares.count(),
        'fecha': date.today()
    }
    html = template.render(context)
    css_url = os.path.join(settings.BASE_DIR, 'proyecto/static/lib/bootstrap-4.6.2-dist/css/bootstrap.min.css')
    pdf = HTML(string=html, base_url=request.build_absolute_uri()).write_pdf()
    return HttpResponse(pdf, content_type='application/pdf')