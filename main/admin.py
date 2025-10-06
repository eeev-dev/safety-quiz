from django.contrib import admin
from .models import EmployeeUser, Answer, Question, Option, Branch, Position, Section, Category, Settings
from django.urls import path
from django.shortcuts import render, redirect
from django import forms
from django.shortcuts import get_object_or_404
from .utils import parse_question_block, parse_russian_date
from docx import Document
from django.contrib.admin import SimpleListFilter
from rangefilter.filters import DateRangeFilter
from datetime import timedelta, datetime
from django.db import IntegrityError
from django.contrib import messages


class PositionInline(admin.TabularInline):
    model = Position
    extra = 1


class OptionInline(admin.TabularInline):
    model = Option
    extra = 0


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


class BranchAdmin(admin.ModelAdmin):
    list_display = ['title']
    inlines = [PositionInline]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    can_delete = False
    show_change_link = False
    readonly_fields = ['question', 'employee_option', "is_correct"]
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    def is_correct(self, obj):
        return obj.employee_option.is_correct if obj.employee_option else None

    is_correct.boolean = True
    is_correct.short_description = 'Правильный ответ'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        all_dates = qs.values_list('date_passed', flat=True).distinct().order_by('-date_passed')

        selected_date = request.GET.get('answer_date')

        if selected_date:
            try:
                selected_date_obj = parse_russian_date(selected_date)
            except ValueError:
                selected_date_obj = None
        else:
            selected_date_obj = all_dates.first()

        if selected_date_obj:
            start = selected_date_obj.replace(second=0, microsecond=0)
            end = start + timedelta(minutes=1)
            qs = qs.filter(date_passed__gte=start, date_passed__lt=end)

        return qs.order_by('number')


class EmployeeAdmin(admin.ModelAdmin):
    fields = ['branch', 'position', 'fio', 'score', 'total', 'number', 'tries']
    list_display = ['branch', 'position', 'fio', 'score', 'total', 'last_date_passed']
    list_filter = [
        'branch',
        ('last_date_passed', DateRangeFilter)
    ]
    search_fields = ['fio']
    inlines = [AnswerInline]

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        answers = Answer.objects.filter(employee_id=object_id)
        dates = answers.values_list('date_passed', flat=True).distinct().order_by('-date_passed')

        selected_date = dates.first() if dates else None

        if selected_date:
            qs = answers.filter(date_passed=selected_date)

            if not isinstance(selected_date, datetime):
                selected_date_obj = parse_russian_date(selected_date)
                start = selected_date_obj.replace(second=0, microsecond=0)
                end = start + timedelta(minutes=1)
                qs = answers.filter(date_passed__gte=start, date_passed__lt=end)

            extra_context['employee_score'] = qs.filter(employee_option__is_correct=True).count()
            extra_context['employee_total'] = qs.count()

            extra_context['available_dates'] = dates
            extra_context['selected_date'] = selected_date

        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    

class SectionAdmin(admin.ModelAdmin):
    list_display = ['title']
    inlines = [CategoryInline]


class UploadForm(forms.Form):
    file = forms.FileField(label="Выберите файл .docx для загрузки")


class HasCorrectFilter(SimpleListFilter):
    title = 'Есть правильный вариант'
    parameter_name = 'has_correct'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Есть'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(options__is_correct=True).distinct()
        elif self.value() == 'no':
            return queryset.exclude(options__is_correct=True).distinct()
        return queryset


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['category', 'question_ru', 'question_kg']
    inlines = [OptionInline]
    list_filter = ['category', HasCorrectFilter]
    search_fields = ['question_ru', 'question_kg']
    change_list_template = "admin/main/question/change_list.html"

    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-questions/", self.admin_site.admin_view(self.parse_from_doc)),
            path("upload-questions/", self.admin_site.admin_view(self.upload_questions), name='upload_questions')
        ]
        return custom_urls + urls
    

    def upload_questions(self, request):
        if request.method == "POST":
            category_id = request.POST.get("category_id")
            category = get_object_or_404(Category, id=category_id)

            question_keys = [key for key in request.POST if key.startswith("question_") and key.endswith("_ru")]
            question_indices = sorted(set(key.split("_")[1] for key in question_keys), key=int)

            for q_idx in question_indices:
                question_ru = request.POST.get(f"question_{q_idx}_ru")
                question_kg = request.POST.get(f"question_{q_idx}_kg")

                option_keys = [key for key in request.POST if key.startswith(f"option_{q_idx}_ru_")]
                option_indices = sorted(set(key.split("_")[-1] for key in option_keys), key=int)

                question, created = Question.objects.get_or_create(
                    category=category,
                    question_ru=question_ru,
                    question_kg=question_kg
                )

                if not created:
                    for opt_idx in option_indices:
                        option_ru = request.POST.get(f"option_{q_idx}_ru_{opt_idx}")
                        option_kg = request.POST.get(f"option_{q_idx}_kg_{opt_idx}")
                        correct = request.POST.get(f"correct_{q_idx}_{opt_idx}")

                        question.options.create(
                            option_ru=option_ru,
                            option_kg=option_kg,
                            is_correct=True if correct == "on" else False
                        )

            messages.success(request, "Вопросы были успешно загружены.")
            return redirect('/admin/main/question')


    def parse_from_doc(self, request):
        if request.method == "POST":
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['file']
                category_id = request.POST.get('category')

                doc = Document(file)
                paragraphs = doc.paragraphs
                results = parse_question_block(paragraphs)
                
                return render(request, "admin/edit_parse_results.html", {
                    "results": list(enumerate(results, 1)),
                    "category_id": category_id,
                })
        else:
            form = UploadForm()

        return render(request, "admin/upload_from_doc.html", {
            "form": form,
            "title": "Загрузить вопросы из документа",
            "sections": Section.objects.all(),
            "categories": Category.objects.none()
        })
    

class SettingsAdmin(admin.ModelAdmin):
    list_display = ['timer', 'questions']
    can_delete = False

    def has_add_permission(self, request):
        return not Settings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Settings, SettingsAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Branch, BranchAdmin)
admin.site.register(EmployeeUser, EmployeeAdmin)