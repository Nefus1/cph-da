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


def test_loader_parses_california_general_poa(loader: TemplateLoader) -> None:
    content = loader.load("california_general_poa", "v1")

    assert content.metadata.doc_type == "california_general_poa"
    assert any(question.id == "poa_durability" for question in content.interview.questions)
    assert any(clause.id == "standard_banking_power" for clause in content.clauses.clauses)


def test_california_general_poa_clause_branching(loader: TemplateLoader) -> None:
    content = loader.load("california_general_poa", "v1")

    resolved = ClauseResolver().resolve(
        content.clauses.clauses,
        {
            "poa_durability": "durable",
            "include_gifting_power": True,
            "principal_in_long_term_care": True,
        },
    )
    resolved_ids = {clause.id for clause in resolved}

    assert "durable_effectiveness" in resolved_ids
    assert "non_durable_effectiveness" not in resolved_ids
    assert "optional_gifting" in resolved_ids
    assert "long_term_care_ombudsman_notice" in resolved_ids


def test_california_msa_with_minor_children_branching(loader: TemplateLoader) -> None:
    composer = JurisdictionPackComposer()
    content = loader.load("california_msa", "v1")

    with_children = composer.compose(content, {"with_minor_children": True})
    with_children_ids = {clause.id for clause in with_children.clauses}

    assert "division_of_property" in with_children_ids
    assert "allocation_of_debts" in with_children_ids
    assert "spousal_support" in with_children_ids
    assert "child_custody_parenting_plan" in with_children_ids
    assert "child_support" in with_children_ids
    assert "no_minor_children_statement" not in with_children_ids
    assert any(question.id == "parenting_plan_summary" for question in with_children.questions)

    without_children = composer.compose(content, {"with_minor_children": False})
    without_children_ids = {clause.id for clause in without_children.clauses}

    assert "child_custody_parenting_plan" not in without_children_ids
    assert "child_support" not in without_children_ids
    assert "no_minor_children_statement" in without_children_ids


def test_california_three_day_notice_locality_pack_selection(loader: TemplateLoader) -> None:
    composer = JurisdictionPackComposer()
    content = loader.load("california_3_day_notice", "v1")

    la_result = composer.compose(
        content,
        {
            "state": "CA",
            "county": "Los Angeles",
            "city": "Los Angeles",
            "rental_type": "market_rate",
            "amount_due": 1200,
        },
    )
    assert la_result.selected_pack_ids == ["ca_base", "la_city_rso"]
    assert any(question.id == "la_registration_number" for question in la_result.questions)
    assert any(clause.id == "la_rso_disclosure_clause" for clause in la_result.clauses)

    sf_result = composer.compose(
        content,
        {
            "state": "CA",
            "county": "San Francisco",
            "city": "San Francisco",
            "rental_type": "market_rate",
            "amount_due": 2200,
        },
    )
    assert sf_result.selected_pack_ids == ["ca_base", "sf_county_pack"]
    assert any(question.id == "sf_rent_board_registration" for question in sf_result.questions)
    assert any(clause.id == "sf_local_compliance_clause" for clause in sf_result.clauses)
