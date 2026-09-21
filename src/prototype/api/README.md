# SupTech API

This FastAPI service is the controlled boundary between the UI and approved
server-side score-export adapters. It defaults to synthetic demo data. Do not
add raw Fannie Mae files, stable loan identifiers, or training samples to this
directory or API responses.

An approved export may be configured only through
`SUPTECH_APPROVED_ALERT_EXPORT` and must pass the field/path validation in
`app/adapters/score_export.py`.

The service includes local development authentication and role-based access.
`platform_admin` and `model_governance` may administer local accounts; role
changes require a reason and confirmation and are recorded in `audit_events`.
