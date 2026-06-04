from django.urls import path
from .views import ResolucionUniversitariaCreateView

urlpatterns = [
    path('ru/', ResolucionUniversitariaCreateView.as_view(), name='crear-resolucion'),
]