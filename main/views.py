from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpRequest
from django.template.response import TemplateResponse

class IndexView(TemplateView):
    template_name = 'main/base.html'  # Главный шаблон

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Можно добавить начальные данные, если нужно
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        # При GET показываем страницу с формой
        return TemplateResponse(request, 'main/employee.html', context)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        branch = request.POST.get('branch')
        position = request.POST.get('position')
        full_name = request.POST.get('fullName')

        # Здесь можно добавить валидацию и сохранение
        errors = {}
        if not branch:
            errors['branch'] = 'Выберите филиал'
        if not position:
            errors['position'] = 'Выберите должность'
        if not full_name:
            errors['fullName'] = 'Введите ФИО'

        if errors:
            context = self.get_context_data(**kwargs)
            context.update({
                'errors': errors,
                'branch': branch,
                'position': position,
                'fullName': full_name,
            })
            # Если это HTMX запрос — возвращаем форму с ошибками в #main-content
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'main/employee.html', context)
            else:
                # Обычный POST — возвращаем форму с ошибками
                return TemplateResponse(request, 'main/employee.html', context)

        # Если ошибок нет — можно сохранить, например:
        # Employee.objects.create(branch=branch, position=position, full_name=full_name)

        # Подготовим контекст для следующего шага (например, выбор билета)
        context = {
            'branch': branch,
            'position': position,
            'full_name': full_name,
            # сюда можно добавить данные для выбора билета
        }

        if request.headers.get('HX-Request'):
            # Возвращаем частичный шаблон с выбором билета, который подгрузится в #main-content
            return TemplateResponse(request, 'main/cards.html', context)
        else:
            # При обычном POST редирект или полный рендер страницы
            return TemplateResponse(request, 'main/cards.html', context)
    

class CardsView(TemplateView):
    template_name = 'main/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return TemplateResponse(request, 'main/cards.html', context)
    

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

