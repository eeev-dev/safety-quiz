from django.urls import path
from .views.employee import IndexView
from .views.language import LanguageView
from .views.test_entry import TestEntryView
from .views.questions import QuestionView
from .views.answers import AnswersView
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