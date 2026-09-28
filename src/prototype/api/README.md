# SupTech API

This FastAPI service is the controlled boundary between the UI and approved
server-side score-export adapters. It defaults to synthetic demo data. Do not
add raw Fannie Mae files, stable loan identifiers, or training samples to this
directory or API responses.

An approved export may be configured only through
`SUPTECH_APPROVED_ALERT_EXPORT` and must pass the field/path validation in
`app/adapters/score_export.py`.

The local Compose configuration mounts a generated de-identified Fannie Mae
research export. It includes no raw loan identifier or feature vector. The
optional `observed_outcome` and `outcome_observed_at` fields are post-window
audit fields, never model inputs. Existing development databases are preserved;
to seed that export into a new local database, create a new Compose volume or
perform an explicitly approved development-data reset.

The service includes local development authentication and role-based access.
`platform_admin` and `model_governance` may administer local accounts; role
changes require a reason and confirmation and are recorded in `audit_events`.
Reviewers may optionally rate SHAP explanation usefulness from 1 to 5. The
aggregated `/api/v1/evaluation/summary` endpoint reports workload, observed-
outcome confirmation, and available explanation ratings; it does not claim that
a prospective user study has been completed.
