from django.db import models


class Employee(models.Model):
    branch = models.CharField("Филиал", max_length=100, default="")
    position = models.CharField("Должность", max_length=100, default="")
    fio = models.CharField("ФИО", max_length=100, default="")
    score = models.IntegerField("Результат", default=0)
    total = models.IntegerField("Всего вопросов", default=10)
    is_passed = models.BooleanField("Попытка теста", default=False)
    date_passed = models.DateTimeField("Дата прохождения", auto_now_add=True)

    def __str__(self):
        return self.fio


class Answer(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='answers')
    question = models.TextField("Вопрос", default="")
    answer = models.TextField("Ответ сотрудника", default="")
    correct_answer = models.TextField("Правильный ответ", default="")

    def __str__(self):
        return self.answer


class Card(models.Model):
    number = models.IntegerField("Номер билета", default=0)

    def __str__(self):
        return self.number


class Question(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='questions')
    question_ru = models.TextField("Вопрос на русском", default="")
    question_kg = models.TextField("Вопрос на кыргызском", default="")
    image = models.ImageField(upload_to='questions/')

    def __str__(self):
        return self.question_ru


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    option_ru = models.TextField("Вариант ответа на русском", default="")
    option_kg = models.TextField("Вариант ответа на кыргызском", default="")
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_ru

class Branch(models.Model):
    title = models.CharField("Название филиала", max_length=100, default="")

    def __str__(self):
        return self.title


class Position(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='positions')
    title = models.CharField("Название должности", max_length=100, default="")

    def __str__(self):
        return self.title
