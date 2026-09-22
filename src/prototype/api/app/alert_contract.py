"""Single safe contract for approved alert exports and browser responses."""

APPROVED_EXPORT_FIELDS = frozenset({
    'alert_id', 'loan_reference', 'cohort', 'reporting_month', 'target',
    'risk_score', 'trigger_threshold', 'tier', 'top_shap_driver',
    'top_shap_contribution', 'review_status', 'expert_decision',
})
OPTIONAL_EXPORT_FIELDS = frozenset({'expert_decision'})
REQUIRED_EXPORT_FIELDS = APPROVED_EXPORT_FIELDS - OPTIONAL_EXPORT_FIELDS
FORBIDDEN_EXPORT_MARKERS = frozenset({
    'loan_id', 'raw_path', 'feature_vector', 'training_sample',
    'servicing_history',
})

# The browser receives only this de-identified alert DTO. Model and data
# versions identify the research artefact but do not expose training data.
BROWSER_ALERT_FIELDS = (
    'alert_id', 'loan_reference', 'cohort', 'reporting_month', 'target',
    'risk_score', 'trigger_threshold', 'tier', 'top_shap_driver',
    'top_shap_contribution', 'review_status', 'expert_decision',
    'model_version', 'data_version',
)


def is_valid_export_columns(columns: set[str]) -> bool:
    """Return whether an approved CSV has the complete, minimal safe schema."""
    return (
        APPROVED_EXPORT_FIELDS.issuperset(columns)
        and not columns.intersection(FORBIDDEN_EXPORT_MARKERS)
        and REQUIRED_EXPORT_FIELDS.issubset(columns)
    )


def serialize_browser_alert(alert, model, data, latest_review) -> dict:
    """Map persistence objects to the only alert shape permitted for the UI."""
    values = {
        'alert_id': alert.alert_id,
        'loan_reference': alert.loan_reference,
        'cohort': alert.cohort,
        'reporting_month': alert.reporting_month,
        'target': alert.target,
        'risk_score': alert.risk_score,
        'trigger_threshold': alert.trigger_threshold,
        'tier': alert.tier,
        'top_shap_driver': alert.top_shap_driver,
        'top_shap_contribution': alert.top_shap_contribution,
        'review_status': alert.review_status,
        'expert_decision': latest_review.decision if latest_review else None,
        'model_version': model.version,
        'data_version': data.version,
    }
    return {field: values[field] for field in BROWSER_ALERT_FIELDS}
