from slugify import slugify
from string import ascii_letters, digits
from random import shuffle
from docx import Document
from docx.shared import RGBColor
import re


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
            "number": i + 1,
            "question": question.question_kg if current_lang == 'kg' else question.question_ru,
            "options": serialize_options(question.options.all(), current_lang)
        }
        for i, question in enumerate(questions)
    ]


def serialize_options(options, current_lang):
    return [
        {
            "id": option.id,
            "option": option.option_kg if current_lang == 'kg' else option.option_ru
        }
        for option in options
    ]


def parse_question_block(paragraphs):
    def split_into_blocks(paragraphs):
        blocks = []
        current_block = []

        for p in paragraphs:
            text = p.text.strip()
            if re.match(r"^\d+\.", text):
                if current_block:
                    blocks.append(current_block)
                current_block = [p]
            else:
                current_block.append(p)

        if current_block:
            blocks.append(current_block)

        return blocks

    all_questions = []

    blocks = split_into_blocks(paragraphs)

    for block in blocks:
        question = {"ru": "", "kg": ""}
        options = []
        option_counter = 1

        for p in block:
            text = p.text.strip()

            if re.match(r"^\d+\.", text):
                ru_part, kg_part = text.split("~", 1)
                if not question["ru"]:
                    question["ru"] = ru_part[3:].strip()
                if not question["kg"]:
                    question["kg"] = kg_part.strip()
            elif re.match(r"^[А-Яа-яA-Za-z]\.", text):
                ru_text = text.split("~")[0].split(".", 1)[-1].strip()
                kg_text = text.split("~")[1].strip() if "~" in text else ""

                is_correct = False
                if p.runs:
                    for run in p.runs:
                        if run.font.highlight_color:
                            is_correct = True
                            break

                options.append({
                    "idx": option_counter,
                    "ru": ru_text,
                    "kg": kg_text,
                    "is_correct": is_correct
                })
                option_counter += 1

        all_questions.append({
            "question": question,
            "options": options
        })

    return all_questions



