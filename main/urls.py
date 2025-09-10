from django.urls import path
from .views import IndexView, CardsView, CardView, AnswersView

app_name = 'main'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('cards', CardsView.as_view(), name='cards'),
    path('card', CardView.as_view(), name='card'),
    path('answers', AnswersView.as_view(), name='answers'),
]