from django.urls import path
from django.views.generic import RedirectView
from .views import (
    RUHistoricasPorCarreraView,
    ResolucionUniversitariaCreateView,
    ResolucionUniversitariaListView,
    ResolucionUniversitariaDetailView,
    ResolucionGestionView,
    VistoListCreateView,
    VistoDetailView,
    VistosPaginaView,
    ResolucionCrearPaginaView,
    ResolucionUniversitariaGenerarPDFView,
    )

urlpatterns = [
    path('', RedirectView.as_view(url='/resoluciones/gestion/'), name='home'),
    path('ru/', ResolucionUniversitariaCreateView.as_view(), name='crear-resolucion'),
    path('ru/list/', ResolucionUniversitariaListView.as_view(), name='listar-resoluciones'),
    path('ru/<int:pk>/', ResolucionUniversitariaDetailView.as_view(), name='detalle-resolucion'),
    path('resoluciones/gestion/', ResolucionGestionView.as_view(), name='ru-gestion'),
    path('resoluciones/vistos/', VistosPaginaView.as_view(), name='vistos-pagina'),
    path('resoluciones/crear/', ResolucionCrearPaginaView.as_view(), name='ru-crear'),
    path('ru/generar-pdf/', ResolucionUniversitariaGenerarPDFView.as_view(), name='ru-generar-pdf'),
    
    path('vistos/', VistoListCreateView.as_view(), name='visto-list-create'),
    path('vistos/<int:pk>/', VistoDetailView.as_view(), name='visto-detail'),
    path('ru-historicas/carrera/<int:carrera_id>/',RUHistoricasPorCarreraView.as_view(),name="ru-historicas-por-carrera"),
]