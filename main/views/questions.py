from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import redirect
import json
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from ..models import EmployeeUser, Branch, Position, Question, Answer, Option, Category, Section, Settings
from django.contrib.auth import login, authenticate
from django.contrib.auth import get_user_model
from django.db.models import F
from ..utils import unique_slugify, passed_test, serialize_questions, serialize_options
from docx import Document
from django.http import FileResponse
import io
from django.utils import translation
import random
from django.db.models import Max
from django.utils import timezone

class QuestionView(TemplateView):
    template_name = 'main/questions.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            category_id = request.POST.get('category')
            category = get_object_or_404(Category, id=category_id)

            date = timezone.now()
            request.user.last_date_passed = date
            request.user.tries -= 1
            request.user.save()

            settings = Settings.load()
            ids = category.questions.values_list('id', flat=True)
            random_ids = random.sample(list(ids), settings.questions)
            questions = Question.objects.filter(id__in=random_ids).order_by('id')

            for i, question in enumerate(questions):
                Answer.objects.create(
                    employee = request.user,
                    question = question,
                    number = i + 1,
                    date_passed = request.user.last_date_passed
                )

            context['start_timer_text'] = f"{settings.timer}:00" if settings.timer > 9 else f"0{settings.timer}:00"
            context['millis'] = {settings.timer} * 60 * 1000
            context['questions'] = serialize_questions(questions, request.user.lang_code)
            return TemplateResponse(request, self.template_name, context)
