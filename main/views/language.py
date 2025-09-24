from django.views.generic import TemplateView
from django.conf import settings
from django.template.response import TemplateResponse
from ..models import Branch
from django.utils import translation

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