from django.urls import path
from .views import (
    ResolucionUniversitariaCreateView,
    ResolucionUniversitariaListView,
    ResolucionUniversitariaDetailView,
    ResolucionGestionView,
    VistoDeResolucionView,
)

urlpatterns = [
    path(
        'ru/',
        ResolucionUniversitariaCreateView.as_view(),
        name='crear-resolucion'
    ),

    path(
        'ru/list/',
        ResolucionUniversitariaListView.as_view(),
        name='listar-resoluciones'
    ),

    path(
        'ru/<int:pk>/',
        ResolucionUniversitariaDetailView.as_view(),
        name='detalle-resolucion'
    ),

    path(
        'resoluciones/gestion/', ResolucionGestionView.as_view(), name='ru-gestion'
    ),

    path(
        'ru/<int:pk>/visto/',
        VistoDeResolucionView.as_view(),
        name='visto-resolucion'
    ),
]