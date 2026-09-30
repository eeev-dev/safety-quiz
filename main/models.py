from django.db import models
from django.contrib.auth.models import AbstractUser


class Settings(models.Model):
    timer = models.IntegerField("Минуты таймера", default=10)
    questions = models.IntegerField("Количество вопросов", default=10)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    class Meta:
        verbose_name = "настройки"
        verbose_name_plural = "Настройки"


class EmployeeUser(AbstractUser):
    branch = models.CharField("Филиал", max_length=100, default="", blank=True)
    position = models.CharField("Должность", max_length=100, default="", blank=True)
    fio = models.CharField("ФИО", max_length=100, null=False, blank=False)
    number = models.CharField("Табельный номер", max_length=10, unique=True, null=False, blank=False)
    tries = models.IntegerField("Попыток сдачи", default=2)
    score = models.IntegerField("Последний результат", default=0)
    total = models.IntegerField("Всего вопросов", default=10)
    last_date_passed = models.DateTimeField("Последняя попытка прохождения теста", blank=True, null=True)
    lang_code = models.CharField("Язык", max_length=3, default='ru')

    def __str__(self):
        return self.fio
    
    class Meta:
        verbose_name = "сотрудника"
        verbose_name_plural = "Сотрудники"


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
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions', verbose_name="Категория") 
    question_ru = models.TextField("Вопрос на русском", blank=False, null=False)
    question_kg = models.TextField("Вопрос на кыргызском", blank=False, null=False)
    image = models.ImageField(upload_to='questions/', blank=True, null=True, verbose_name="Изображение")

    def __str__(self):
        return self.question_ru
    
    class Meta:
        verbose_name = "вопрос"
        verbose_name_plural = "Вопросы"

        constraints = [
            models.UniqueConstraint(fields=['category', 'question_ru', 'question_kg'], name='unique_category_question_ru_kg')
        ]


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_ru = models.TextField("Вариант ответа на русском", null=False, blank=False)
    option_kg = models.TextField("Вариант ответа на кыргызском", blank=False, null=False)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_ru
    
    class Meta:
        verbose_name = "вариант ответа"
        verbose_name_plural = "Варианты ответа"


class Answer(models.Model):
    employee = models.ForeignKey(EmployeeUser, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name="Вопрос")
    employee_option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='answers', null=True, verbose_name="Ответ сотрудника")
    number = models.IntegerField("Номер вопроса", null=True)
    date_passed = models.DateTimeField("Дата прохождения", blank=True, null=True)

    def __str__(self):
        return str(self.employee_option.option_ru) if self.employee_option else "Без ответа"
    
    class Meta:
        verbose_name = "ответ"
        verbose_name_plural = "Ответы"


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
