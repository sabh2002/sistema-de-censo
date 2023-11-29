from django.contrib import admin
from django.urls import path
from censo import views
from censo.views import configurar_usuario
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.inicio, name='inicio'),
    path('ingresar/', views.iniciar_sesion, name='ingresar'),
    path('configurar/', configurar_usuario, name='configurar'),
    path('registrar/', views.registrar_usuario, name='registrar'),
    path('habitantes/', views.HabitantesListView.as_view(), name='habitantes'),
    path('habitantes/crear', views.crear_habitantes.as_view(), name='crear_habitantes'),
    path('jefes/crear', views.JefeFamiliarCrear.as_view(), name='crear_jefe'),
    path('cargas/crear', views.CargaFamiliarCrear.as_view(), name='crear_carga'),
    path('cargas/', views.CargaFamiliarList.as_view(), name='carga_familiar'),
    path('jefes/', views.JefeFamiliarList.as_view(), name='jefes_familia'),
    path('cerrar-sesion/', auth_views.LogoutView.as_view(), name='cerrar_sesion'),
    path('habitantes/editar/<int:pk>/', views.editar_habitantes.as_view(), name='editar_habitante'),
    path('jefes/editar/<int:jefe_id>/', views.JefeFamiliarEditar.as_view(), name='editar_jefe'),
    path('cargas/editar/<int:carga_id>', views.CargaFamiliarEditar.as_view(), name='editar_carga'),
    path('jefes/eliminar/<int:pk>/', views.EliminarJefeFamiliar.as_view(), name='eliminar_jefe'),
    path('habitantes/eliminar/<int:pk>/', views.EliminarHabitante.as_view(), name='eliminar_habitante'),
    path('cargas/eliminar/<int:pk>/', views.EliminarCargaFamiliar.as_view(), name='eliminar_carga' ),
    path('habitantes/niños/', views.MostrarNiños.as_view(), name='mostrar_niños'),
    path('habitantes/ancianos/', views.MostrarAncianos.as_view(), name='mostrar_ancianos'),
    path('habitantes/discapacitados', views.MostrarDiscapacitados.as_view(), name='mostrar_discapacitados'),
    path('habitantes/hombres', views.MostrarHombres.as_view(), name='mostrar_hombres'),
    path('habitantes/mujeres', views.MostrarMujeres.as_view(), name='mostrar_mujeres'),
    #path('habitantes/pdf', views.HabitantesPDF.as_view(), name='habitantes_pdf'),
    path('habitantes/pdf', views.HabitantesPDF, name='habitantes_pdf'),
    path('jefes/pdf/<int:pk>/', views.JefePDF.as_view(), name='jefe_pdf'),
    path('jefes/carga_jefe/<int:jefe_id>', views.CargasJefe.as_view(), name='carga_jefe'),
    path('habitantes/mujeres_embarazadas', views.MostrarEmbarazadas.as_view(), name='mujeres_embarazadas'),
    path('habitantes/votantes/', views.MostrarVotante.as_view(),name='votantes'),
    path('habitantes/vivientes/', views.MostrarVivientes.as_view(),name='vivientes'),
    path('jefes/pdf/', views.JefesPDF, name= 'jefes_pdf'),
    path('cargas/pdf', views.CargasPDF,name= 'cargas_pdf'),
    path('niños/pdf/', views.NiñosPDF,name= 'niños_pdf'),
    path('ancianos/pdf', views.AncianosPDF,name= 'ancianos_pdf'),
    path('discapacitados/pdf/', views.DiscapacitadosPDF, name='discapacitados_pdf'),
    path('mujeres/pdf', views.MujeresPDF, name='mujeres_pdf'),
    path('hombres/pdf', views.HombresPDF, name='hombres_pdf'),
    path('embarazadas/pdf/', views.EmbarazadasPDF, name='embarazadas_pdf'),
    path('votantes/pdf/', views.VotantesPDF, name='votantes_pdf'),
    path('viviendas/pdf', views.ViviendasPDF, name= 'viviendas_pdf'),
    

    
]
