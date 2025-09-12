from django.urls import path
from .views import IndexView, CardsView, CardView
from django.conf import settings
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('cards', CardsView.as_view(), name='cards'),
    path('card', CardView.as_view(), name='card'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)