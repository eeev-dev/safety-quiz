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