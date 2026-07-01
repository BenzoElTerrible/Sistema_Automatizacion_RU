from django.urls import path
from django.views.generic import RedirectView
from .views import ResolucionCrearPaginaView, ResolucionUniversitariaGenerarPDFView

urlpatterns = [
    path('', RedirectView.as_view(url='/resoluciones/gestion/'), name='home'),
    path('resoluciones/crear/', ResolucionCrearPaginaView.as_view(), name='ru-crear'),
    path('ru/generar-pdf/', ResolucionUniversitariaGenerarPDFView.as_view(), name='ru-generar-pdf'),
]