from django.views.generic import TemplateView
from docx import Document
from django.http import FileResponse
import io

class AnswersView(TemplateView):
    template_name = 'main/answers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get(self, request, *args, **kwargs):
        user = request.user
        answers = user.answers.filter(date_passed=request.user.last_date_passed).order_by('id')

        if user.lang_code == 'ru':
            doc = Document()
            doc.add_heading('Информация о сотруднике', 0)
            doc.add_paragraph(f'ФИО: {user.fio}')
            doc.add_paragraph(f'Филиал: {user.branch}')
            doc.add_paragraph(f'Должность: {user.position}')
            doc.add_paragraph(f'Правильных ответов: {user.score} из {user.total}')
            doc.add_paragraph(f'Дата прохождения: {user.last_date_passed.strftime('%d.%m.%Y %H:%M')}')
            doc.add_paragraph('С результатами ознакомлен(-а): ______________')

            doc.add_heading('Ответы на вопросы', level=1)
            doc.add_paragraph('')
            for answer in answers:
                doc.add_paragraph(answer.question, style='List Number')
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
            doc.add_paragraph(f'Туура жооптордун саны: {user.score} / {user.total}')
            doc.add_paragraph(f'Өткөн күнү: {user.last_date_passed.strftime('%d.%m.%Y %H:%M')}')
            doc.add_paragraph('Жыйынтыгы менен тааныштым: ______________')

            doc.add_heading('Суроолорго берилген жооптор', level=1)
            doc.add_paragraph('')
            for answer in answers:
                doc.add_paragraph(answer.question, style='List Number')
                doc.add_paragraph(f'Туура жооп: {answer.correct_answer}')
                doc.add_paragraph(f'Кызматкердин жообу: {answer.answer}')

            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            filename = f"Жыйынтык_{user.fio.replace(' ', '_')}.docx"
            response = FileResponse(buffer, as_attachment=True, filename=filename)
            return response