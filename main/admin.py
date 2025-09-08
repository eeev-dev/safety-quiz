from django.contrib import admin
from .models import Employee, Answer, Card, Question, Option, Branch, Position
import nested_admin


class PositionInline(admin.TabularInline):
    model = Position
    extra = 1


class OptionInline(nested_admin.NestedTabularInline):
    model = Option
    extra = 4


class QuestionInline(nested_admin.NestedTabularInline):
    model = Question
    inlines = [OptionInline]
    extra = 1


class CardAdmin(nested_admin.NestedModelAdmin):
    list_display = ['number']
    inlines = [QuestionInline]


class BranchAdmin(admin.ModelAdmin):
    list_display = ['title']
    inlines = [PositionInline]


class PositionAdmin(admin.ModelAdmin):
    list_display = ['title']


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['branch', 'position', 'fio', 'score', 'total', 'is_passed', 'date_passed']
    list_filter = ['branch', 'fio', 'is_passed', 'date_passed']


class AnswerAdmin(admin.ModelAdmin):
    list_display = ['employee', 'question', 'answer', 'correct_answer']


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_ru', 'question_kg', 'image']
    inlines = [OptionInline]


class OptionAdmin(admin.ModelAdmin):
    list_display = ['option_ru', 'option_kg', 'is_correct']


admin.site.register(Branch, BranchAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Option, OptionAdmin)