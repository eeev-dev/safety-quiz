from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import redirect
import json
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from .models import EmployeeUser, Branch, Position, Question, Answer, Option, Category, Section
from django.contrib.auth import login, authenticate
from django.contrib.auth import get_user_model
from django.db.models import F
from .utils import unique_slugify, passed_test, serialize_question, serialize_options
from docx import Document
from django.http import FileResponse
import io
from datetime import datetime
from django.utils import translation
import random

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

                    employee.username = user_slug
                    employee.branch = branch.title
                    employee.position = position

                    lang_code = request.COOKIES.get('django_language')
                    if lang_code:
                        employee.lang_code = lang_code
                    employee.set_password('secure123')
                    employee.save()

                    user = authenticate(username=user_slug, password='secure123')
                    login(request, user)

                if user.tries > 0:
                    context['sections'] = Section.objects.all()
                    context['categories'] = Category.objects.none()
                    return TemplateResponse(request, 'main/test_entry.html', context)
                else:
                    context['employee'] = user
                    context['answers'] = user.answers.all()
                    context['is_passed'] = passed_test(user.score, user.total)
                    return TemplateResponse(request, 'main/answers.html', context)
                
            else:
                context['branches'] = Branch.objects.all()
                context['positions'] = Position.objects.none()

                context['sections'] = Section.objects.all()
                context['categories'] = Category.objects.none()

                response = TemplateResponse(request, 'main/employee.html', context)
        
                if request.user.is_authenticated:
                    lang_code = request.user.lang_code
                    translation.activate(lang_code)
                    request.session[settings.LANGUAGE_COOKIE_NAME] = lang_code
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
                
                return response
    

class LanguageView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(*kwargs)
        return TemplateResponse(request, 'main/language.html', context)
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(*kwargs)
        if request.headers.get('HX-Request'):
            lang_code = request.POST.get('lang')
            translation.activate(lang_code)
            request.session[settings.LANGUAGE_COOKIE_NAME] = lang_code

            if request.user.is_authenticated:
                request.user.lang_code = lang_code
                request.user.save()

            context['branches'] = Branch.objects.all()
            response = TemplateResponse(request, 'main/employee.html', context)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
            return response
        

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


class QuestionView(TemplateView):
    template_name = 'main/questions.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
    

'''class CardsView(TemplateView):
    template_name = 'main/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            context['cards'] = Card.objects.all().order_by('number')
            return TemplateResponse(request, 'main/partials/card.html', context)
        
    def post(self, request: HttpRequest, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if (request.headers.get('HX_Request')):
            card_id = request.GET.get("id")
            card = get_object_or_404(Card, id=card_id)
            questions = card.questions.order_by('id').all()

            request.user.date_passed = datetime.now()
            request.user.card_number = card.number
            request.user.total = questions.count()
            saved_questions = request.user.answers.values_list('question')
            for i, q in enumerate(questions):
                if q.question_ru not in saved_questions:
                    correct_option = q.options.filter(is_correct=True).first()
                    if request.user.lang_code == 'ru':
                        Answer.objects.create(
                            employee = request.user,
                            question = f"{i + 1}. {q.question_ru}",
                            answer = "Ответ не был выбран",
                            correct_answer = correct_option.option_ru if correct_option else "Правильный ответ не указан"
                        )
                    else:
                        Answer.objects.create(
                            employee = request.user,
                            question = f"{i + 1}. {q.question_kg}",
                            answer = "Жооп тандалган жок",
                            correct_answer = correct_option.option_kg if correct_option else "Туура жооп көрсөтүлгөн эмес"
                        )
            request.user.save()

            question = questions.first()
            options = question.options.all()
            context['question_number'] = 1
            context['card_number'] = card.number
            context['current_question'] = serialize_question(question, request.user.lang_code)
            context['options'] = serialize_options(options, request.user.lang_code)
            return TemplateResponse(request, 'main/questions.html', context)'''
    

class CardView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        option_id = request.GET.get('answer')
        if option_id:
            option = get_object_or_404(Option, id=option_id)
            question = option.question
            if request.user.lang_code == 'ru':
                for answer in request.user.answers.all():
                    if answer.question[3:] == question.question_ru:
                        answer.answer = option.option_ru
                        answer.save()

                        if answer.correct_answer == option.option_ru:
                            request.user.score += 1
                            request.user.save()

                        break
            else:
                for answer in request.user.answers.all():
                    if answer.question[3:] == question.question_kg:
                        answer.answer = option.option_kg
                        answer.save()

                        if answer.correct_answer == option.option_kg:
                            request.user.score += 1
                            request.user.save()

                        break

        answers = request.user.answers.all()
        context['employee'] = request.user
        context['answers'] = answers
        context['is_passed'] = passed_test(request.user.score, answers.count())
        return TemplateResponse(request, 'main/answers.html', context)
        
    
    '''def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            option_id = request.POST.get('answer')
            option = get_object_or_404(Option, id=option_id)
            question = option.question
            # card = question.card

            if request.user.lang_code == 'ru':
                for answer in request.user.answers.all():
                    if answer.question[3:] == question.question_ru:
                        answer.answer = option.option_ru
                        answer.save()

                        if answer.correct_answer == option.option_ru:
                            request.user.score += 1
                            request.user.save()

                        break
            else:
                for answer in request.user.answers.all():
                    if answer.question[3:] == question.question_kg:
                        answer.answer = option.option_kg
                        answer.save()

                        if answer.correct_answer == option.option_kg:
                            request.user.score += 1
                            request.user.save()

                        break
                
            questions = card.questions.order_by('id')
            current_index = 0
            for i, q in enumerate(questions):
                if q.id == question.id:
                    current_index = i + 1
                    break

            if current_index < len(questions):
                context['is_last_question'] = False
                if current_index + 1 == len(questions):
                    context['is_last_question'] = True
                question = questions[current_index]
                context['question_number'] = current_index + 1
                # context['card_number'] = card.number
                context['current_question'] = serialize_question(question, request.user.lang_code)
                context['options'] = serialize_options(question.options.all(), request.user.lang_code)
                return TemplateResponse(request, 'main/partials/question.html', context)
            else:
                answers = request.user.answers.all()
                correct_answers = answers.filter(answer=F('correct_answer'))
                context['employee'] = request.user
                context['answers'] = answers
                context['is_passed'] = passed_test(correct_answers.count(), answers.count())
                return TemplateResponse(request, 'main/answers.html', context)
'''
            
    
class AnswersView(TemplateView):
    template_name = 'main/answers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get(self, request, *args, **kwargs):
        user = request.user
        answers = user.answers.all()

        if user.lang_code == 'ru':
            doc = Document()
            doc.add_heading('Информация о сотруднике', 0)
            doc.add_paragraph(f'ФИО: {user.fio}')
            doc.add_paragraph(f'Филиал: {user.branch}')
            doc.add_paragraph(f'Должность: {user.position}')
            # doc.add_paragraph(f'Билет: №{user.card_number}')
            doc.add_paragraph(f'Правильных ответов: {user.score} из {user.total}')
            doc.add_paragraph(f'Дата прохождения: {user.last_date_passed.strftime('%d.%m.%Y %H.%M')}')

            doc.add_heading('Ответы на вопросы', level=1)
            for answer in answers:
                doc.add_paragraph(answer.question[3:], style='List Number')
                doc.add_paragraph(f'Правильный ответ: {answer.correct_answer}')
                doc.add_paragraph(f'Ответ сотрудника: {answer.answer}')

            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            filename = f"Результаты_{user.fio.replace(' ', '_')}.docx"
            response = FileResponse(buffer, as_attachment=True, filename=filename)
            return response
        else:
            doc = Document()
            doc.add_heading('Кызматкер жөнүндө маалымат', 0)
            doc.add_paragraph(f'Толук аты-жөнү: {user.fio}')
            doc.add_paragraph(f'Филиал: {user.branch}')
            doc.add_paragraph(f'Кызматы: {user.position}')
            # doc.add_paragraph(f'Билет: №{user.card_number}')
            doc.add_paragraph(f'Туура жооптордун саны: {user.score} / {user.total}')
            doc.add_paragraph(f'Өткөн күнү: {user.last_date_passed.strftime('%d.%m.%Y %H.%M')}')

            doc.add_heading('Суроолорго берилген жооптор', level=1)
            for answer in answers:
                doc.add_paragraph(answer.question[3:], style='List Number')
                doc.add_paragraph(f'Туура жооп: {answer.correct_answer}')
                doc.add_paragraph(f'Кызматкердин жообу: {answer.answer}')

            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            filename = f"Жыйынтык_{user.fio.replace(' ', '_')}.docx"
            response = FileResponse(buffer, as_attachment=True, filename=filename)
            return response


