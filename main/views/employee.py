from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.conf import settings
from django.http import HttpRequest
from django.template.response import TemplateResponse
from ..models import EmployeeUser, Branch, Position, Category, Section, Settings, Question
from django.contrib.auth import login, authenticate
from ..utils import unique_slugify, passed_test
from django.utils import translation


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
            context['positions'] = positions
            return TemplateResponse(request, 'main/partials/position_options.html', context)
        
        tabel_number = request.GET.get('number')
        if tabel_number:
            employee = EmployeeUser.objects.filter(number=tabel_number).first()
            if employee:
                return JsonResponse({'full_name': employee.fio})
            else:
                return JsonResponse({'full_name': 'Сотрудник с таким табельным номером не найден'})

        response = TemplateResponse(request, 'main/employee.html', context)
        
        if request.user.is_authenticated:
            lang_code = request.user.lang_code
            translation.activate(lang_code)
            request.session[settings.LANGUAGE_COOKIE_NAME] = lang_code
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        
        return response
    

    def post(self, request: HttpRequest, *args, **kwargs):
        if request.headers.get('HX-Request'):
            context = self.get_context_data(**kwargs)

            branch_id = request.POST.get('branch_id')
            position = request.POST.get('position')
            full_name = request.POST.get('fullName')
            number = request.POST.get('number')

            if full_name != 'Сотрудник с таким табельным номером не найден':
                branch = get_object_or_404(Branch, id=branch_id)
                employee = EmployeeUser.objects.filter(number__icontains=number).first()

                user = authenticate(username=employee.username, password="secure123")
                if user is not None:
                    login(request, user)
                    
                    lang_code = request.COOKIES.get('django_language')
                    if lang_code:
                        user.lang_code = lang_code
                        user.save()
                    
                    user.branch = branch.title
                    user.position = position
                    user.save()
                else:
                    user_slug = unique_slugify(full_name)

                    employee.branch = branch.title
                    employee.position = position

                    lang_code = request.COOKIES.get('django_language')
                    if lang_code:
                        employee.lang_code = lang_code

                    employee.username = user_slug
                    employee.set_password('secure123')
                    employee.save()

                    user = authenticate(username=user_slug, password='secure123')
                    login(request, user)
        
                if user.tries > 0:
                    user.score = 0
                    settings = Settings.load()
                    user.total = settings.questions
                    user.save()
                    context['sections'] = Section.objects.all()
                    context['categories'] = Category.objects.none()
                    return TemplateResponse(request, 'main/test_entry.html', context)
                else:
                    answers = []
                    lang = request.user.lang_code or 'ru'
                    employee_answers = request.user.answers.filter(date_passed=request.user.last_date_passed)
                    
                    for answer in employee_answers:
                        question = answer.question
                        correct_option = question.options.filter(is_correct=True).first()

                        question_text = getattr(question, f'question_{lang}', '')
                        selected_text = getattr(answer.employee_option, f'option_{lang}', None) if answer.employee_option else None
                        correct_text = getattr(correct_option, f'option_{lang}', None) if correct_option else None

                        answers.append({
                            'number': answer.number,
                            'question': question_text,
                            'selected_answer': selected_text,
                            'correct_answer': correct_text,
                        })

                    context['employee'] = user
                    context['answers'] = sorted(answers, key=lambda x: x['number'])
                    context['is_passed'] = passed_test(user.score, user.total)
                    return TemplateResponse(request, 'main/answers.html', context)
                
            else:
                context['branches'] = Branch.objects.all()
                context['positions'] = Position.objects.none()

                context['sections'] = Section.objects.all()
                context['categories'] = Category.objects.none()

                response = TemplateResponse(request, self.template_name, context)
        
                if request.user.is_authenticated:
                    lang_code = request.user.lang_code
                    translation.activate(lang_code)
                    request.session[settings.LANGUAGE_COOKIE_NAME] = lang_code
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
                
                return response