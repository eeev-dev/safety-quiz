from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import redirect
import json
from django.http import HttpResponseBadRequest, HttpRequest
from django.template.response import TemplateResponse
from .models import Employee, Branch, Position, Card, Question

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
            employees = Employee.objects.all().filter(
                fio__icontains=full_name,
                branch__icontains=branch.title,
                position__icontains=position
            )

            if employees.exists():
                if employees.first().card_number > 0:
                    return TemplateResponse(request, 'main/answers.html', context)
                else:
                    return TemplateResponse(request, 'main/cards.html', context)
            else:
                Employee.objects.create(
                    branch=branch, 
                    position=position, 
                    fio=full_name
                )
                return TemplateResponse(request, 'main/cards.html', context)
    

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
            try:
                card_id = request.POST.get('id')
                context['questions'] = Question.objects.all().filter(card_id=card_id)
                return TemplateResponse(request, 'main/question.html', context)
            except json.JSONDecodeError:
                return HttpResponseBadRequest('Invalid JSON')
    

class CardView(TemplateView):
    template_name = 'main/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return TemplateResponse(request, 'main/question.html', context)
    

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
    


