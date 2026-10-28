from typing import Any


class IssueFindingEvidence:
    def __init__(
        self,
        page_url: str,
        observed_value: str = "",
        expected_value: str = "",
        evidence_snippet: str = "",
        evidence_type: str = "html_element",
        explanation: str = "",
        page_id: str | None = None,
    ):
        self.page_url = page_url
        self.observed_value = observed_value
        self.expected_value = expected_value
        self.evidence_snippet = evidence_snippet
        self.evidence_type = evidence_type
        self.explanation = explanation
        self.page_id = page_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_url": self.page_url,
            "observed_value": self.observed_value,
            "expected_value": self.expected_value,
            "evidence_snippet": self.evidence_snippet,
            "evidence_type": self.evidence_type,
            "explanation": self.explanation,
            "page_id": self.page_id,
        }


class CheckResult:
    def __init__(
        self,
        issue_code: str,
        title: str,
        category: str,
        severity: str,
        impact: float,
        confidence: float,
        estimated_effort: float,
        description: str,
        why_it_matters: str,
        suggested_fix: str,
        example_fix: str | None = None,
        priority_reason: str | None = None,
        evidences: list[IssueFindingEvidence] | None = None,
    ):
        self.issue_code = issue_code
        self.title = title
        self.category = category
        self.severity = severity  # critical, high, medium, low, informational
        self.impact = impact  # 0.0 to 1.0
        self.confidence = confidence  # 0.0 to 1.0
        self.estimated_effort = estimated_effort  # 0.0 to 1.0 (lower is easier)
        self.description = description
        self.why_it_matters = why_it_matters
        self.suggested_fix = suggested_fix
        self.example_fix = example_fix
        self.priority_reason = priority_reason
        self.evidences = evidences if evidences is not None else []

    @property
    def affected_page_count(self) -> int:
        return len(self.evidences)
