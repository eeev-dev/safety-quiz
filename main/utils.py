from slugify import slugify
from string import ascii_letters, digits
from random import shuffle

def unique_slugify(full_name):
    chars = list(ascii_letters + digits)
    shuffle(chars)
    return slugify(full_name) + ''.join(chars[:3])


def passed_test(correct_answers: int, total_questions: int) -> bool:
    if total_questions == 0:
        return False
    percentage = (correct_answers / total_questions) * 100
    return percentage >= 70


def serialize_questions(questions, current_lang):
    return [
        {
            "id": question.id,
            "number": question.number,
            "question": question.question_kg if current_lang == 'kg' else question.question_ru,
            "options": serialize_options(question.options.all(), current_lang)
        }
        for question in questions
    ]
    

def serialize_options(options, current_lang):
    return [
        {
            "id": option.id,
            "option": option.option_kg if current_lang == 'kg' else option.option_ru
        }
        for option in options
    ]


