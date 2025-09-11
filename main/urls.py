from django.urls import path
from .views import IndexView, CardsView, CardView

app_name = 'main'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('cards', CardsView.as_view(), name='cards'),
    path('card', CardView.as_view(), name='card'),
]