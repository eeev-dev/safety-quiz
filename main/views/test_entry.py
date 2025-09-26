from django.views.generic import TemplateView
from django.template.response import TemplateResponse
from ..models import Category, Section, Question, Answer
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
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            category_id = request.POST.get('category')
            category = get_object_or_404(Category, id=category_id)

            date = timezone.now()
            request.user.last_date_passed = date
            request.user.tries -= 1
            request.user.save()

            ids = category.questions.values_list('id', flat=True)
            random_ids = random.sample(list(ids), 10)
            questions = Question.objects.filter(id__in=random_ids).order_by('id')

            for question in questions:
                correct_option = question.options.filter(is_correct=True).first()

                if request.user.lang_code == 'ru':
                    Answer.objects.create(
                        employee = request.user,
                        question = question.question_ru,
                        answer = "Ответ не был выбран",
                        correct_answer = correct_option.option_ru if correct_option else "Правильный ответ был не указан",
                        date_passed = date
                    )
                else:
                    Answer.objects.create(
                        employee = request.user,
                        question = question.question_kg,
                        answer = "Жооп тандалган жок",
                        correct_answer = correct_option.option_kg if correct_option else "Туура жооп көрсөтүлгөн эмес",
                        date_passed = date
                    )

            context['questions'] = serialize_questions(questions, request.user.lang_code)
            return TemplateResponse(request, 'main/questions.html', context)