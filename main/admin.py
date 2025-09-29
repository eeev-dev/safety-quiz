from django.contrib import admin
from .models import EmployeeUser, Answer, Question, Option, Branch, Position, Section, Category, Settings
from django.core.exceptions import ValidationError


class PositionInline(admin.TabularInline):
    model = Position
    extra = 1


class OptionInline(admin.TabularInline):
    model = Option
    extra = 0


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    can_delete = False
    show_change_link = False
    readonly_fields = ['question', 'correct_answer', 'answer', "is_correct"]
    max_num = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    def is_correct(self, obj):
        return obj.answer == obj.correct_answer
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-date_passed').order_by('number')


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


class BranchAdmin(admin.ModelAdmin):
    list_display = ['title']
    inlines = [PositionInline]


class EmployeeAdmin(admin.ModelAdmin):
    fields = ['branch', 'position', 'fio', 'score', 'total', 'last_date_passed', 'number', 'tries']
    list_display = ['branch', 'position', 'fio', 'score', 'total', 'last_date_passed']
    list_filter = ['branch', 'last_date_passed']
    search_fields = ['fio']
    inlines = [AnswerInline]
    

class SectionAdmin(admin.ModelAdmin):
    list_display = ['title']
    inlines = [CategoryInline]


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['category', 'question_ru', 'question_kg', 'image']
    inlines = [OptionInline]
    list_filter = ['category']
    search_fields = ['question_ru', 'question_kg']


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