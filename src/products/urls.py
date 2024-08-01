from django.urls import path
from .views import ImportData, DetailView

urlpatterns = [
    path('import/', ImportData.as_view(), name='import-data'),
    path('detail/<str:model_name>/', DetailView.as_view(), name='model-list'),
    path('detail/<str:model_name>/<int:id>/', DetailView.as_view(), name='model-detail'),
]
