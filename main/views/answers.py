from django.views.generic import TemplateView
from docx import Document
from django.http import FileResponse
import io
from ..utils import passed_test
from ..models import Option, Question
from django.utils.timezone import localtime
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.template.response import TemplateResponse

class AnswersView(TemplateView):
    template_name = 'main/answers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get(self, request, *args, **kwargs):
        user = request.user
        answers = user.answers.filter(date_passed=request.user.last_date_passed).order_by('id')
        local_dt = localtime(user.last_date_passed)

        if user.lang_code == 'ru':
            doc = Document()
            doc.add_heading('Информация о сотруднике', 0)
            doc.add_paragraph(f'ФИО: {user.fio}')
            doc.add_paragraph(f'Филиал: {user.branch}')
            doc.add_paragraph(f'Должность: {user.position}')
            doc.add_paragraph(f'Правильных ответов: {user.score} из {user.total}')
            doc.add_paragraph(f'Дата прохождения: {local_dt.strftime('%d.%m.%Y %H:%M')}')
            doc.add_paragraph(f'Табельный номер: {user.number}')
            doc.add_paragraph(f'Результат: {"Пройден" if passed_test(user.score, user.total) else "Не пройден"}')
            doc.add_paragraph('С результатами ознакомлен(-а): ______________')

            doc.add_heading('Ответы на вопросы', level=1)
            doc.add_paragraph('')
            for answer in answers:
                correct_answer = answer.question.options.filter(is_correct=True).first()
                
                doc.add_paragraph(answer.question.question_ru, style='List Number')
                if answer.employee_option:
                    doc.add_paragraph(f'Ваш ответ: {answer.employee_option.option_ru}')
                else:
                    doc.add_paragraph(f'Ваш ответ: Ответ не был  выбран')
                doc.add_paragraph(f'Правильный ответ: {correct_answer.option_ru if correct_answer else "Правильный ответ не найден"}')

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
            doc.add_paragraph(f'Туура жооптордун саны: {user.score} / {user.total}')
            doc.add_paragraph(f'Өткөн күнү: {local_dt.strftime('%d.%m.%Y %H:%M')}')
            doc.add_paragraph(f'Табелдик номер: {user.number}')
            doc.add_paragraph(f'Жыйынтык: {"Өттү" if passed_test(user.score, user.total) else "Өтпөй калды"}')
            doc.add_paragraph('Жыйынтыгы менен тааныштым: ______________')

            doc.add_heading('Суроолорго берилген жооптор', level=1)
            doc.add_paragraph('')
            for answer in answers:
                correct_answer = answer.question.options.filter(is_correct=True).first()
                
                doc.add_paragraph(answer.question.question_kg, style='List Number')
                if answer.employee_option:
                    doc.add_paragraph(f'Сиздин жообу: {answer.employee_option.option_kg}')
                else:
                    doc.add_paragraph(f'Сиздин жообу: Жооп тандалган жок')
                doc.add_paragraph(f'Туура жооп: {correct_answer.employee_option_kg if correct_answer else "Туура жооп көрсөтүлгөн эмес"}')

            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            filename = f"Жыйынтык_{user.fio.replace(' ', '_')}.docx"
            response = FileResponse(buffer, as_attachment=True, filename=filename)
            return response
        

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

        employee_answers = request.user.answers.filter(date_passed=request.user.last_date_passed)
        answers = []

        score = request.user.score
        lang = request.user.lang_code or 'ru'

        for question_id, option_id in selected_options.items():
            question = get_object_or_404(Question, id=question_id)
            correct_option = question.options.filter(is_correct=True).first()
            selected_option = question.options.filter(id=option_id).first()

            employee_answer = employee_answers.filter(question_id=question_id).first()
            if employee_answer:
                employee_answer.employee_option = selected_option
                employee_answer.save()

                if correct_option and correct_option.id == option_id:
                    score += 1

        request.user.score = score
        request.user.save()

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


        context['employee'] = request.user
        context['answers'] = sorted(answers, key=lambda x: x['number'])
        context['is_passed'] = passed_test(request.user.score, request.user.total)
        return TemplateResponse(request, self.template_name, context)