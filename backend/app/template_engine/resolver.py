from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.template_engine.expression import SafeBooleanEvaluator
from app.template_engine.models import ClauseDefinition, ComposedJurisdictionPack, InterviewQuestion, TemplateContent


class ClauseResolver:
    def __init__(self, evaluator: SafeBooleanEvaluator | None = None):
        self.evaluator = evaluator or SafeBooleanEvaluator()

    def resolve(self, clauses: list[ClauseDefinition], answers: Mapping[str, Any]) -> list[ClauseDefinition]:
        by_id = {clause.id: clause for clause in clauses}
        selected_ids: set[str] = set()

        for clause in clauses:
            include = clause.default_included
            if clause.include_when:
                include = self.evaluator.evaluate(clause.include_when, answers)
            if include:
                selected_ids.add(clause.id)

        changed = True
        while changed:
            changed = False
            for clause_id in list(selected_ids):
                clause = by_id[clause_id]
                for dep in clause.depends_on:
                    if dep not in by_id:
                        raise ValueError(f"Clause '{clause.id}' depends on unknown clause '{dep}'")
                    if dep not in selected_ids:
                        selected_ids.add(dep)
                        changed = True

        for clause in clauses:
            if clause.id not in selected_ids or not clause.exclusive_group:
                continue
            for other in clauses:
                if (
                    other.id in selected_ids
                    and other.id != clause.id
                    and other.exclusive_group == clause.exclusive_group
                ):
                    if clause.id < other.id:
                        selected_ids.discard(other.id)

        return [clause for clause in clauses if clause.id in selected_ids]


class JurisdictionPackComposer:
    def __init__(self, evaluator: SafeBooleanEvaluator | None = None):
        self.evaluator = evaluator or SafeBooleanEvaluator()

    def compose(self, content: TemplateContent, answers: Mapping[str, Any]) -> ComposedJurisdictionPack:
        packs_by_id = {pack.id: pack for pack in content.metadata.jurisdiction.packs}
        selected_ids = [content.metadata.jurisdiction.base_pack]

        for pack in content.metadata.jurisdiction.packs:
            if pack.id == content.metadata.jurisdiction.base_pack:
                continue
            if pack.include_when and self.evaluator.evaluate(pack.include_when, answers):
                selected_ids.append(pack.id)

        selected_ids = sorted(set(selected_ids))
        selected_packs = [packs_by_id[pack_id] for pack_id in selected_ids]

        questions = list(content.interview.questions)
        validations = []
        clauses = list(content.clauses.clauses)
        disclosures: list[str] = []

        for pack in selected_packs:
            questions.extend(pack.questions)
            validations.extend(pack.validations)
            clauses.extend(pack.clauses)
            disclosures.extend(pack.disclosures)

        questions = _dedupe_by_id(questions)
        validations = _dedupe_by_id(validations)
        clauses = _dedupe_by_id(clauses)
        disclosures = list(dict.fromkeys(disclosures))

        visible_questions = [
            question
            for question in questions
            if not question.visible_when or self.evaluator.evaluate(question.visible_when, answers)
        ]

        resolved_clauses = ClauseResolver(self.evaluator).resolve(clauses=clauses, answers=answers)

        return ComposedJurisdictionPack(
            selected_pack_ids=selected_ids,
            questions=visible_questions,
            validations=validations,
            clauses=resolved_clauses,
            disclosures=disclosures,
        )


def _dedupe_by_id(items: list[Any]) -> list[Any]:
    seen: dict[str, Any] = {}
    for item in items:
        seen[item.id] = item
    return list(seen.values())
