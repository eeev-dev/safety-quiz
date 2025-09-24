from django.db import models
from django.contrib.auth.models import AbstractUser


class EmployeeUser(AbstractUser):
    branch = models.CharField("Филиал", max_length=100, default="")
    position = models.CharField("Должность", max_length=100, default="")
    fio = models.CharField("ФИО", max_length=100, default="")
    number = models.CharField("Табельный номер", max_length=10, unique=True)
    tries = models.IntegerField("Попыток сдачи", default=2)
    score = models.IntegerField("Результат", default=0)
    total = models.IntegerField("Всего вопросов", default=10)
    last_date_passed = models.DateTimeField("Последняя попытка прохождения теста", blank=True, null=True)
    lang_code = models.CharField("Язык", max_length=3, default='ru')

    def __str__(self):
        return self.fio
    
    class Meta:
        verbose_name = "сотрудника"
        verbose_name_plural = "Сотрудники"
    

class Answer(models.Model):
    employee = models.ForeignKey(EmployeeUser, on_delete=models.CASCADE, related_name='answers')
    question = models.TextField("Вопрос", default="")
    answer = models.TextField("Ответ сотрудника", default="", blank=True, null=True)
    correct_answer = models.TextField("Правильный ответ", default="")
    date_passed = models.DateTimeField("Дата прохождения", blank=True, null=True)

    def __str__(self):
        return self.answer
    
    class Meta:
        verbose_name = "ответ"
        verbose_name_plural = "Ответы"


class Section(models.Model):
    title = models.CharField("Раздел", max_length=100, default="")

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "раздел"
        verbose_name_plural = "Разделы"


class Category(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='categories')
    title = models.CharField("Категория", max_length=100, default="")
    
    def __str__(self):
        return f"{self.title} ({self.section.title})"
    
    class Meta:
        verbose_name = "категория сотрудников"
        verbose_name_plural = "Категория сотрудников"


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name='questions') 
    question_ru = models.TextField("Вопрос на русском", default="")
    question_kg = models.TextField("Вопрос на кыргызском", default="", blank=True, null=True)
    image = models.ImageField(upload_to='questions/', blank=True, null=True)

    def __str__(self):
        return self.question_ru
    
    class Meta:
        verbose_name = "вопрос"
        verbose_name_plural = "Вопросы"


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_ru = models.TextField("Вариант ответа на русском", default="")
    option_kg = models.TextField("Вариант ответа на кыргызском", default="", blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_ru
    
    class Meta:
        verbose_name = "вариант ответа"
        verbose_name_plural = "Варианты ответа"


class Branch(models.Model):
    title = models.CharField("Название филиала", max_length=100, default="")

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "филиал"
        verbose_name_plural = "Филиалы"


class Position(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='positions')
    title = models.CharField("Название должности", max_length=100, default="")

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "должность"
        verbose_name_plural = "Должности"
