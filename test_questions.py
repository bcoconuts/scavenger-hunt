"""Tests for the Question class"""

from questions import Question

def test_check_answer_exact_match():
    q = Question(
        question="What color is the sky?",
        answer="Blue",
        fake_answers=["Red", "Yellow", "Orange"]
    )
    assert q.check_answer("Blue") is True


def test_check_answer_is_case_sensetive():
    q = Question(
        question="What color is the sky?",
        answer="Blue",
        fake_answers=["Red", "Yellow", "Orange"]
    )
    assert q.check_answer("blue") is True
    assert q.check_answer("BLUE") is True


def test_check_answer_ignores_whitespace():
    q = Question(
        question="What color is the sky?",
        answer="Blue",
        fake_answers=["Red", "Yellow", "Orange"]
    )
    assert q.check_answer("   Blue   ") is True


def test_check_answer_returns_false_for_wrong_answer():
    q = Question(
        question="What color is the sky?",
        answer="Blue",
        fake_answers=["Red", "Yellow", "Orange"]
    )
    assert q.check_answer("Red") is False


def test_all_choices_shuffled_contains_correct_answer():
    q = Question(
        question="What color is the sky?",
        answer="Blue",
        fake_answers=["Red", "Yellow", "Orange"]
    )
    answer_set = q.all_choices_shuffled
    assert "Blue" in answer_set


def test_all_choices_shuffled_contains_all_four_options():
    q = Question(
        question="What color is the sky?",
        answer="Blue",
        fake_answers=["Red", "Yellow", "Orange"]
    )
    answer_set = q.all_choices_shuffled
    assert answer_set == {"Red", "Yellow", "Orange", "Blue"}