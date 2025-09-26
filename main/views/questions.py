from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import redirect
import json
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from ..models import EmployeeUser, Branch, Position, Question, Answer, Option, Category, Section
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

class QuestionView(TemplateView):
    template_name = 'main/questions.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        selected_options = {}
        for key, value in request.POST.items():
            if key.startswith('answer'):
                try:
                    question_id = int(key.replace('answer_', ''))
                    option_id = int(value)
                    selected_options[question_id] = option_id
                except ValueError:
                    continue

        answers = request.user.answers.filter(date_passed=request.user.last_date_passed)

        for question_id, option_id in selected_options.items():
            option = get_object_or_404(Option, id=option_id)
            question = option.question
            correct_option = question.options.filter(is_correct=True).first()

            if request.user.lang_code == 'ru':
                answer = answers.filter(question=question.question_ru).first()
                
                if answer:
                    answer.answer = option.option_ru
                    answer.save()
                    
                    if correct_option:
                        if option.option_ru == correct_option.option_ru:
                            request.user.score += 1
                            request.user.save()

            elif request.user.lang_code == 'kg':
                answer = answers.filter(question=question.question_kg).first()
                
                if answer:
                    answer.answer = option.option_kg
                    answer.save()
                    
                    if correct_option:
                        if option.option_kg == correct_option.option_kg:
                            request.user.score += 1
                            request.user.save()

        context['employee'] = request.user
        context['answers'] = answers.order_by('id')
        context['is_passed'] = passed_test(request.user.score, request.user.total)
        return TemplateResponse(request, 'main/answers.html', context)

