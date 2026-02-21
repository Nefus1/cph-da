from pathlib import Path

import pytest

from app.template_engine import (
    ClauseResolver,
    JurisdictionPackComposer,
    SafeBooleanEvaluator,
    TemplateLoader,
    UnsafeExpressionError,
)


@pytest.fixture
def loader() -> TemplateLoader:
    return TemplateLoader(Path(__file__).resolve().parents[1] / "templates")


def test_loader_parses_three_day_notice(loader: TemplateLoader) -> None:
    content = loader.load("three_day_notice", "v1")
    assert content.metadata.doc_type == "three_day_notice"
    assert any(question.id == "county" for question in content.interview.questions)
    assert any(clause.id == "rent_demand" for clause in content.clauses.clauses)


def test_safe_boolean_evaluator_rejects_code_execution() -> None:
    evaluator = SafeBooleanEvaluator()
    with pytest.raises(UnsafeExpressionError):
        evaluator.evaluate('__import__("os").system("echo hacked")', {})


def test_clause_resolution_supports_inclusion_dependencies_and_exclusive_groups(loader: TemplateLoader) -> None:
    content = loader.load("three_day_notice", "v1")
    resolved = ClauseResolver().resolve(content.clauses.clauses, {"county": "Los Angeles"})
    resolved_ids = {clause.id for clause in resolved}

    assert "rent_demand" in resolved_ids
    assert "service_method" in resolved_ids
    assert "la_translation" in resolved_ids
    assert "sf_translation" not in resolved_ids


def test_jurisdiction_pack_composition_is_deterministic(loader: TemplateLoader) -> None:
    composer = JurisdictionPackComposer()
    content = loader.load("three_day_notice", "v1")

    result = composer.compose(content, {"state": "CA", "county": "San Francisco", "amount_due": 900})

    assert result.selected_pack_ids == ["ca_base", "sf_local"]
    assert any(question.id == "sf_rent_board_registration" for question in result.questions)
    assert all(validation.id != "amount_positive" or validation.expression == "amount_due > 0" for validation in result.validations)
    assert "San Francisco Rent Ordinance disclosure." in result.disclosures
