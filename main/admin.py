from django.contrib import admin
from .models import EmployeeUser, Answer, Card, Question, Option, Branch, Position
import nested_admin
from django.core.exceptions import ValidationError


class PositionInline(admin.TabularInline):
    model = Position
    extra = 1


class OptionInline(nested_admin.NestedTabularInline):
    model = Option
    extra = 0


class QuestionInline(nested_admin.NestedTabularInline):
    model = Question
    inlines = [OptionInline]
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


class CardAdmin(nested_admin.NestedModelAdmin):
    list_display = ['number']
    inlines = [QuestionInline]

    def save_model(self, request, obj, form, change):
        if obj.number == 0:
            raise ValidationError("Нельзя присваивать билету номер 0")
        super().save_model(request, obj, form, change)


class BranchAdmin(admin.ModelAdmin):
    list_display = ['title']
    inlines = [PositionInline]


class EmployeeAdmin(admin.ModelAdmin):
    fields = ['branch', 'position', 'fio', 'score', 'total', 'card_number', 'date_passed']
    list_display = ['branch', 'position', 'fio', 'score', 'total', 'card_number', 'date_passed']
    list_filter = ['branch', 'date_passed']
    search_fields = ['fio']
    inlines = [AnswerInline]

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(Branch, BranchAdmin)
admin.site.register(EmployeeUser, EmployeeAdmin)
admin.site.register(Card, CardAdmin)