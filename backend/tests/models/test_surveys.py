"""Test cases for survey models."""

import pytest

from app.models.surveys import Survey, Question, QuestionOption, NextQuestionCondition
from app.models.types import QuestionType, ConditionOperator
from app.core.exceptions import BusinessRuleError


def test_validate_multiple_choice_question():
    """Test that multiple choice questions must have options."""
    # Should raise error when no options provided
    with pytest.raises(BusinessRuleError, match="Multiple choice questions must have options"):
        question = Question(
            id="q1",
            type=QuestionType.MULTIPLE_CHOICE,
            text="Test question",
            options=[],
            is_terminal=False,
        )
        question.validate_options()

    # Should pass with options
    question = Question(
        id="q1",
        type=QuestionType.MULTIPLE_CHOICE,
        text="Test question",
        options=[
            QuestionOption(id="opt1", text="Option 1"),
            QuestionOption(id="opt2", text="Option 2"),
        ],
        is_terminal=False,
    )
    assert question.validate_options()


def test_validate_survey_flow():
    """Test survey flow validation."""
    # Valid survey
    survey = Survey(
        title="Test Survey",
        description="Test Description",
        first_question_id="q1",
        questions={
            "q1": Question(
                id="q1",
                type=QuestionType.MULTIPLE_CHOICE,
                text="First question",
                options=[
                    QuestionOption(id="opt1", text="Yes", next_question_id="q2"),
                    QuestionOption(id="opt2", text="No", next_question_id="q3"),
                ],
                is_terminal=False,
            ),
            "q2": Question(
                id="q2",
                type=QuestionType.TEXT,
                text="Second question",
                is_terminal=True,
            ),
            "q3": Question(
                id="q3",
                type=QuestionType.TEXT,
                text="Third question",
                is_terminal=True,
            ),
        },
    )
    assert survey.validate_survey_flow()

    # Invalid survey - missing first question
    with pytest.raises(BusinessRuleError, match="First question not found"):
        invalid_survey = Survey(
            title="Test Survey",
            description="Test Description",
            first_question_id="missing",
            questions={
                "q1": Question(
                    id="q1",
                    type=QuestionType.TEXT,
                    text="Question",
                    is_terminal=True,
                ),
            },
        )
        invalid_survey.validate_survey_flow()

    # Invalid survey - circular reference
    with pytest.raises(BusinessRuleError, match="Circular reference detected"):
        circular_survey = Survey(
            title="Test Survey",
            description="Test Description",
            first_question_id="q1",
            questions={
                "q1": Question(
                    id="q1",
                    type=QuestionType.MULTIPLE_CHOICE,
                    text="First question",
                    options=[QuestionOption(id="opt1", text="Yes", next_question_id="q2")],
                    is_terminal=False,
                ),
                "q2": Question(
                    id="q2",
                    type=QuestionType.MULTIPLE_CHOICE,
                    text="Second question",
                    options=[QuestionOption(id="opt1", text="Back", next_question_id="q1")],
                    is_terminal=False,
                ),
            },
        )
        circular_survey.validate_survey_flow()


def test_question_response_validation():
    """Test question response validation."""
    question = Question(
        id="q1",
        type=QuestionType.MULTIPLE_CHOICE,
        text="Test question",
        options=[
            QuestionOption(id="opt1", text="Option 1"),
            QuestionOption(id="opt2", text="Option 2"),
        ],
        is_terminal=False,
    )

    # Valid response
    assert question.get_validated_response("opt1") == "opt1"

    # Invalid option
    with pytest.raises(BusinessRuleError, match="Invalid option"):
        question.get_validated_response("invalid")

    # Test boolean validation
    bool_question = Question(
        id="q2",
        type=QuestionType.BOOLEAN,
        text="Yes/No question",
        is_terminal=False,
    )
    with pytest.raises(BusinessRuleError, match="Boolean response must be 'yes' or 'no'"):
        bool_question.get_validated_response("maybe")

    # Test number validation
    num_question = Question(
        id="q3",
        type=QuestionType.NUMBER,
        text="Number question",
        is_terminal=False,
    )
    assert num_question.get_validated_response("42") == 42.0
    with pytest.raises(BusinessRuleError, match="Number must be a valid integer or float"):
        num_question.get_validated_response("not a number")


def test_conditional_next_question():
    """Test conditional next question logic."""
    q1 = Question(
        id="q1",
        type=QuestionType.NUMBER,
        text="Age question",
        conditional_next=[
            NextQuestionCondition(
                operator=ConditionOperator.EQUALS,
                value=18,
                next_question_id="adult"
            ),
            NextQuestionCondition(
                operator=ConditionOperator.EQUALS,
                value=17,
                next_question_id="minor"
            ),
        ],
        default_next_question_id="default",
        is_terminal=False,
    )

    # Test conditional routing
    assert q1.get_next_question("18") == "adult"
    assert q1.get_next_question("17") == "minor"
    # Should return None if no condition is met
    assert q1.get_next_question("20") is None


    q2 = Question(
        id="q2",
        type=QuestionType.NUMBER,
        text="Age question",
        default_next_question_id="default",
        is_terminal=False,
    )

    assert q2.get_next_question("20") == "default"


def test_validate_next_questions():
    """Test validation of next question references."""
    available_questions = {"q1", "q2", "q3", "q4"}

    # Test default next question validation
    question = Question(
        id="q1",
        type=QuestionType.TEXT,
        text="Test question",
        default_next_question_id="q2",
        is_terminal=False,
    )
    assert question.validate_next_questions(available_questions)

    # Test invalid default next question
    with pytest.raises(BusinessRuleError, match="Question invalid_q not found"):
        question = Question(
            id="q1",
            type=QuestionType.TEXT,
            text="Test question",
            default_next_question_id="invalid_q",
            is_terminal=False,
        )
        question.validate_next_questions(available_questions)

    # Test options next question validation
    question = Question(
        id="q1",
        type=QuestionType.MULTIPLE_CHOICE,
        text="Test question",
        options=[
            QuestionOption(id="opt1", text="Option 1", next_question_id="q2"),
            QuestionOption(id="opt2", text="Option 2", next_question_id="q3"),
        ],
        is_terminal=False,
    )
    assert question.validate_next_questions(available_questions)

    # Test invalid option next question
    with pytest.raises(BusinessRuleError, match="Question invalid_q not found"):
        question = Question(
            id="q1",
            type=QuestionType.MULTIPLE_CHOICE,
            text="Test question",
            options=[
                QuestionOption(id="opt1", text="Option 1", next_question_id="invalid_q"),
            ],
            is_terminal=False,
        )
        question.validate_next_questions(available_questions)

    # Test conditional next validation
    question = Question(
        id="q1",
        type=QuestionType.NUMBER,
        text="Test question",
        conditional_next=[
            NextQuestionCondition(
                operator=ConditionOperator.EQUALS,
                value=42,
                next_question_id="q2"
            ),
        ],
        is_terminal=False,
    )
    assert question.validate_next_questions(available_questions)

    # Test invalid conditional next
    with pytest.raises(BusinessRuleError, match="Question invalid_q not found"):
        question = Question(
            id="q1",
            type=QuestionType.NUMBER,
            text="Test question",
            conditional_next=[
                NextQuestionCondition(
                    operator=ConditionOperator.EQUALS,
                    value=42,
                    next_question_id="invalid_q"
                ),
            ],
            is_terminal=False,
        )
        question.validate_next_questions(available_questions)

    # Test terminal question with next question (should be valid)
    question = Question(
        id="q1",
        type=QuestionType.TEXT,
        text="Test question",
        default_next_question_id="q2",
        is_terminal=True,  # Terminal questions can have next_question_id
    )
    assert question.validate_next_questions(available_questions)

    # Test option with conditions
    question = Question(
        id="q1",
        type=QuestionType.MULTIPLE_CHOICE,
        text="Test question",
        options=[
            QuestionOption(
                id="opt1", 
                text="Option 1", 
                next_question_id="q2",
                conditions=[
                    NextQuestionCondition(
                        operator=ConditionOperator.EQUALS,
                        value=True,
                        next_question_id="q3"
                    )
                ]
            ),
        ],
        is_terminal=False,
    )
    assert question.validate_next_questions(available_questions)

    # Test invalid option condition next question
    with pytest.raises(BusinessRuleError, match="Question invalid_q not found"):
        question = Question(
            id="q1",
            type=QuestionType.MULTIPLE_CHOICE,
            text="Test question",
            options=[
                QuestionOption(
                    id="opt1", 
                    text="Option 1",
                    next_question_id="q2",
                    conditions=[
                        NextQuestionCondition(
                            operator=ConditionOperator.EQUALS,
                            value=True,
                            next_question_id="invalid_q"
                        )
                    ]
                ),
            ],
            is_terminal=False,
        )
        question.validate_next_questions(available_questions)
