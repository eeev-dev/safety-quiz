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
from ..utils import unique_slugify, passed_test, serialize_question, serialize_options
from docx import Document
from django.http import FileResponse
import io
from datetime import datetime
from django.utils import translation
import random

class QuestionView(TemplateView):
    template_name = 'main/questions.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)