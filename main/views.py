from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import redirect
import json
from django.http import HttpResponseBadRequest, HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from .models import EmployeeUser, Branch, Position, Card, Question, Answer, Option
from django.contrib.auth import login, authenticate
from slugify import slugify
from django.contrib.auth import get_user_model
from string import ascii_letters, digits
from random import shuffle

User = get_user_model()

class IndexView(TemplateView):
    template_name = 'main/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        context['positions'] = Position.objects.none()

        branch_id = request.GET.get("branch_id")
        if branch_id and request.headers.get("HX-Request"):
            positions = Position.objects.filter(branch_id=branch_id)
            return TemplateResponse(request, 'main/partials/position_options.html', {'positions': positions})

        return TemplateResponse(request, 'main/employee.html', context)
    

    def post(self, request: HttpRequest, *args, **kwargs):
        if request.headers.get('HX-Request'):
            context = self.get_context_data(**kwargs)

            branch_id = request.POST.get('branch_id')
            position = request.POST.get('position')
            full_name = request.POST.get('fullName')

            branch = get_object_or_404(Branch, id=branch_id)
            employees = EmployeeUser.objects.filter(
                fio__icontains=full_name,
                branch=branch,
                position__icontains=position
            )

            if employees.exists():
                employee = employees.first()
                print(employee.user_slug)
                user = authenticate(username=employee.user_slug, password="secure123")
                if user is not None:
                    login(request, user)
                    if employee.card_number > 0:
                        return TemplateResponse(request, 'main/answers.html', context)
                    else:
                        return TemplateResponse(request, 'main/cards.html', context)
            else:
                chars = list(ascii_letters + digits)
                shuffle(chars)
                user_slug = slugify(full_name) + ''.join(chars[:3])
                print(user_slug)
                user = User.objects.create_user(
                    username=user_slug,
                    branch=branch.title, 
                    position=position, 
                    fio=full_name,
                    user_slug=user_slug
                )
                user.set_password('secure123')
                user.save()
                user = authenticate(username=user_slug, password='secure123')
                return TemplateResponse(request, 'main/cards.html', context)
        
        return HttpResponse('Ошибка входа')
    

class CardsView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('HX-Request'):
            context = self.get_context_data(**kwargs)
            context['cards'] = Card.objects.all()
            return TemplateResponse(request, 'main/partials/card.html', context)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        if (request.headers.get('HX_Request')):
            context = self.get_context_data(**kwargs)
            card_id = request.POST.get('id')
            context['card_id'] = card_id
            return TemplateResponse(request, 'main/questions.html', context)
    

class CardView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            option_id = request.GET.get('answer')
            option = get_object_or_404(Option, id=option_id)
            question = option.question
            card = question.card    
            questions = card.questions.order_by('id')

            current_index = 0
            for i, q in enumerate(questions):
                if str(q.id) == question.id:
                    current_index = i + 1
                    break

            if current_index >= len(questions):
                context['card_number'] = card.number
                context['current_question'] = question
                context['options'] = Option.objects.filter(question=question)
                return TemplateResponse(request, 'main/questions.html', context)
            else:
                return TemplateResponse(request, 'main/answers.html', context)

    def post(self, request: HttpRequest, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if (request.headers.get('HX_Request')):
            card_id = request.POST.get("card_id")
            card = get_object_or_404(Card, id=card_id)
            question = Question.objects.filter(card=card).order_by('id').first()
            context['card_number'] = card.number
            context['current_question'] = question
            context['options'] = Option.objects.filter(question=question)
            return TemplateResponse(request, 'main/questions.html', context)
                    

class AnswersView(TemplateView):
    template_name = 'main/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return TemplateResponse(request, 'main/answers.html', context)
    
    
class AnnouncementView(TemplateView):
    template_name = 'main/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return TemplateResponse(request, 'main/announcement.html', context)
    


