from django.urls import path
from .views import VistoListCreateView, VistoDetailView, VistosPaginaView

urlpatterns = [
    path('vistos/', VistoListCreateView.as_view(), name='visto-list-create'),
    path('vistos/<int:pk>/', VistoDetailView.as_view(), name='visto-detail'),
    path('resoluciones/vistos/', VistosPaginaView.as_view(), name='vistos-pagina'),
]