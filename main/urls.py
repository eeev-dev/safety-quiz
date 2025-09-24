from django.urls import path
from .views import IndexView, CardView, AnswersView, LanguageView, TestEntryView, QuestionView
from django.conf import settings
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('language', LanguageView.as_view(), name='language'),
    path('test-entry', TestEntryView.as_view(), name='test-entry'),
    path('questions', QuestionView.as_view(), name='questions'),
    path('answers', AnswersView.as_view(), name='answers'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)