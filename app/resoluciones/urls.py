from django.urls import path
from django.views.generic import RedirectView
from .views import (
    ResolucionUniversitariaCreateView,
    ResolucionUniversitariaListView,
    ResolucionUniversitariaDetailView,
    ResolucionGestionView,
    VistosDeRUView,
    VistoListCreateView,
    VistoDetailView,
    VistosPaginaView,
)

urlpatterns = [
    path('', RedirectView.as_view(url='/resoluciones/gestion/'), name='home'),
    path('ru/', ResolucionUniversitariaCreateView.as_view(), name='crear-resolucion'),
    path('ru/list/', ResolucionUniversitariaListView.as_view(), name='listar-resoluciones'),
    path('ru/<int:pk>/', ResolucionUniversitariaDetailView.as_view(), name='detalle-resolucion'),
    path('ru/<int:pk>/vistos/', VistosDeRUView.as_view(), name='vistos-ru'),
    path('resoluciones/gestion/', ResolucionGestionView.as_view(), name='ru-gestion'),
    path('resoluciones/vistos/', VistosPaginaView.as_view(), name='vistos-pagina'),
    path('vistos/', VistoListCreateView.as_view(), name='visto-list-create'),
    path('vistos/<int:pk>/', VistoDetailView.as_view(), name='visto-detail'),
]