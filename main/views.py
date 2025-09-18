from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import redirect
import json
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from .models import EmployeeUser, Branch, Position, Card, Question, Answer, Option
from django.contrib.auth import login, authenticate
from django.contrib.auth import get_user_model
from django.db.models import F
from .utils import unique_slugify, passed_test, serialize_question, serialize_options
from docx import Document
from django.http import FileResponse
import io
from datetime import datetime
from django.utils import translation

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

            branch = get_object_or_404(Branch, id=branch_id)
            employees = EmployeeUser.objects.filter(
                fio__icontains=full_name,
                branch=branch,
                position__icontains=position
            )

            if employees.exists():
                employee = employees.first()
                user = authenticate(username=employee.user_slug, password="secure123")
                if user is not None:
                    login(request, user)
                    lang_code = request.COOKIES.get('django_language')
                    if lang_code:
                        user.lang_code = lang_code
                        user.save()
                    if employee.card_number > 0:
                        context['employee'] = user
                        context['answers'] = user.answers.all()
                        context['is_passed'] = passed_test(user.score, user.total)
                        return TemplateResponse(request, 'main/answers.html', context)
                    else:
                        return TemplateResponse(request, 'main/cards.html', context)
            else:
                user_slug = unique_slugify(full_name)
                user = User.objects.create_user(
                    username=user_slug,
                    branch=branch.title, 
                    position=position, 
                    fio=full_name,
                    user_slug=user_slug
                )

                lang_code = request.COOKIES.get('django_language')
                if lang_code:
                    user.lang_code = lang_code
                user.set_password('secure123')
                user.save()

                user = authenticate(username=user_slug, password='secure123')
                login(request, user)
            
                return TemplateResponse(request, 'main/cards.html', context)
        
        return HttpResponse('Ошибка входа')
    

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
            context['branches'] = Branch.objects.all()
            
            request.session[settings.LANGUAGE_COOKIE_NAME] = lang_code
            response = TemplateResponse(request, 'main/employee.html', context)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
            return response
        

class CardsView(TemplateView):
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
            context['option_id'] = options[0]
            context['question_number'] = 1
            context['card_number'] = card.number
            context['current_question'] = serialize_question(question, request.user.lang_code)
            context['options'] = serialize_options(options, request.user.lang_code)
            return TemplateResponse(request, 'main/questions.html', context)
    

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
        
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            option_id = request.POST.get('answer')
            option = get_object_or_404(Option, id=option_id)
            question = option.question
            card = question.card

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
                context['card_number'] = card.number
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
            doc.add_paragraph(f'Билет: №{user.card_number}')
            doc.add_paragraph(f'Правильных ответов: {user.score} из {user.total}')
            doc.add_paragraph(f'Дата прохождения: {user.date_passed.strftime('%d.%m.%Y %H.%M')}')

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
            doc.add_paragraph(f'Билет: №{user.card_number}')
            doc.add_paragraph(f'Туура жооптордун саны: {user.score} / {user.total}')
            doc.add_paragraph(f'Өткөн күнү: {user.date_passed.strftime('%d.%m.%Y %H.%M')}')

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


