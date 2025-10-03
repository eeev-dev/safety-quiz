from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from ..models import Category, Section, Question, Answer, Settings
from django.shortcuts import get_object_or_404
import random
from ..utils import serialize_questions
from django.utils import timezone

class TestEntryView(TemplateView):
    template_name = 'main/test_entry.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs) 
        
        section_id = request.GET.get("section_id")
        if section_id and request.headers.get("HX-Request"):
            categories = Category.objects.filter(section_id=section_id)
            context['sections'] = Section.objects.all()
            context['categories'] = categories
            return TemplateResponse(request, 'main/partials/category_options.html', context)

        return TemplateResponse(request, self.template_name, context)