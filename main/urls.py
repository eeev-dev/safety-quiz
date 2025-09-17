from django.urls import path
from .views import IndexView, CardsView, CardView, AnswersView, LanguageView
from django.conf import settings
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('language', LanguageView.as_view(), name='language'),
    path('cards', CardsView.as_view(), name='cards'),
    path('card', CardView.as_view(), name='card'),
    path('answers', AnswersView.as_view(), name='answers'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)