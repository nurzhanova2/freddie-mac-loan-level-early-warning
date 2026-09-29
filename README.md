<div align="center">

# Explainable SupTech Early-Warning System

### A research prototype for early detection of borrower deterioration

<p><a href="README.md"><strong>English</strong></a> · <a href="README_ru.md">Русский</a></p>

<p>
  <img src="https://img.shields.io/badge/status-research%20prototype-183153?style=flat-square" alt="Research prototype">
  <img src="https://img.shields.io/badge/data-Fannie%20Mae%20Primary-168697?style=flat-square" alt="Fannie Mae Primary">
  <img src="https://img.shields.io/badge/stack-React%20%2B%20FastAPI%20%2B%20PostgreSQL-2D7DD2?style=flat-square" alt="Technology stack">
  <img src="https://img.shields.io/badge/use-research%20only-6B7280?style=flat-square" alt="Research use only">
</p>

<p>
  <a href="#quick-start">Quick start</a> ·
  <a href="#research-results">Research results</a> ·
  <a href="#suptech-workflow">Workflow</a> ·
  <a href="#roles-and-access">Roles</a> ·
  <a href="#security-boundaries">Security</a> ·
  <a href="#repository-map">Repository map</a>
</p>

</div>

> **Research boundary.** This dissertation prototype prioritises cases for
> human review. It does not approve, decline, sanction, or otherwise automate
> credit or supervisory decisions.

```text
data → risk score → alert → explanation → risk trigger → expert review
```

It operationalises explainable early warning at the loan-month level through
time-aware validation, control of information leakage, calibrated probabilities,
capacity-based Red/Amber alerts, local SHAP explanations, and an auditable
review workflow.

<p align="center">
  <img src="docs/assets/screenshots/suptech/research-overview.png" alt="Research overview" width="48%">
  <img src="docs/assets/screenshots/suptech/alert-queue.png" alt="Red and Amber alert queue" width="48%">
</p>

## What is included

| Layer | Repository content |
|---|---|
| Research data workflow | Fannie Mae ingestion, quality checks, cohort panels, outcome construction, leakage register, manifests, and reproducible reports |
| Models | Logistic Regression and XGBoost baselines; horizon, training-size, Q1/Q3, calibration, and explainability experiments |
| Evidence | EDA, temporal validation, metrics, trigger policy, SHAP, permutation importance, ALE, figures, and bilingual chapters |
| SupTech prototype | React interface, FastAPI, PostgreSQL audit trail, RBAC, administration, and Docker Compose |
| Transferability boundary | Freddie Mac remains a separate workflow for future external validation after field harmonisation |

## Quick start

### Start the complete prototype

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and
run from the repository root:

```bash
docker compose up --build
```

| Service | Address | Purpose |
|---|---|---|
| Web application | <http://localhost:5173> | Research evidence and SupTech workflow |
| API documentation | <http://localhost:8000/docs> | FastAPI OpenAPI / Swagger documentation |
| PostgreSQL | `localhost:5432` | Local users, reviews, and audit events |

```bash
docker compose down
```

### Sign in

The sign-in page supports **RU / EN**. All local demonstration accounts use:

```text
demo-password-change-me
```

| Role | Demonstration login | Primary capability |
|---|---|---|
| Research viewer | `demo_research_viewer` | View research evidence, alerts, and explanations |
| Risk analyst | `demo_risk_analyst` | Review alerts and save expert decisions |
| Model governance | `demo_model_governance` | Review alerts, inspect the registry/audit trail, administer users |
| Data steward | `demo_data_steward` | Inspect alerts, registry, and audit trail; no user administration |
| Platform administrator | `demo_platform_admin` | Administer users and access research screens; alert data are intentionally unavailable |

Use **Sign out** in the header before testing another role.

## Research results

The primary v01 models use Fannie Mae Q1 cohorts, a time-based split, and a
six-month prediction horizon. OOT was not used for fitting, calibration,
threshold selection, or hyperparameter selection of that baseline.

| Outcome | Leading model | OOT ROC-AUC | OOT PR-AUC | Operational policy |
|---|---|---:|---:|---|
| `formal_adverse_6m` | XGBoost | **0.8943** | **0.2866** | Red: top 1%; 24.29% precision; 50.09% recall |
| `early_deterioration_6m` | XGBoost | **0.7310** | **0.0663** | Amber: top 5%; 8.69% precision; 18.59% recall |

<details>
<summary><strong>Open the experimental evidence register</strong></summary>
<br>

- 3-, 6-, and 12-month horizon comparison;
- natural-rate training-size sensitivity at 1%, 5%, 10%, and 25%;
- Q1/Q3 cohort comparison and explanation stability;
- SHAP, permutation importance, and ALE diagnostics;
- Logistic Regression, XGBoost, CatBoost, LightGBM, and pre-specified hybrid
  comparison experiments in the Q1+Q3 research contour.
- completed v02 Q1+Q3 tree-model governance experiment: 18 validation fits,
  validation-only calibration, and one OOT evaluation. The active registry was
  not changed; see the [final governance decision table](fannie_mae/reports/tree_hyperparameter_selection_v01/tree_oot_governance_decision_v01.csv).

Detailed artifacts: [`fannie_mae/reports/`](fannie_mae/reports/) ·
[`fannie_mae/docs/`](fannie_mae/docs/).

</details>

## SupTech workflow

```text
Fannie Mae research data
        │
        ▼
eligible as-of-date features ──► calibrated model score
                                        │
                                        ▼
                             Red / Amber queue policy
                                        │
                                        ▼
                         local SHAP explanation + metadata
                                        │
                                        ▼
                    expert review + audit event + observed outcome
```

1. Open **Alert Queue** and filter by Red/Amber tier or review status.
2. Open **Alert Details** to inspect score, threshold, data/model version,
   observation date, and local SHAP explanation.
3. Under `risk_analyst` or `model_governance`, record a human decision.
4. Under `model_governance` or `data_steward`, inspect the corresponding event
   in **Model Governance → Audit trail**.

<p align="center">
  <img src="docs/assets/screenshots/suptech/alert-detail.png" alt="Alert detail with local SHAP explanation" width="48%">
  <img src="docs/assets/screenshots/suptech/risk-monitoring.png" alt="Risk monitoring view" width="48%">
</p>

## Roles and access

| Action | Viewer | Analyst | Governance | Steward | Admin |
|---|:---:|:---:|:---:|:---:|:---:|
| View research evidence | ✓ | ✓ | ✓ | ✓ | ✓ |
| View alerts and explanations | ✓ | ✓ | ✓ | ✓ | — |
| Save expert review | — | ✓ | ✓ | — | — |
| Inspect registry and audit trail | — | — | ✓ | ✓ | — |
| Create, change, deactivate users | — | — | ✓ | — | ✓ |

Safeguards: users cannot alter their own role or active status; every access
change requires a reason and confirmation; the final active `platform_admin`
cannot be demoted or deactivated.

## Security boundaries

| Protected element | Policy |
|---|---|
| Raw Fannie Mae files | Never served to the browser |
| Loan IDs and full feature vectors | Never exposed through the alert API |
| Browser data contract | Safe alert DTO only: pseudonymous reference, score, tier, versions, concise explanation, review state, and eligible observed outcome |
| Research data connection | Server-side adapter reads pre-approved safe score exports only |
| Automated action | Explicitly prohibited; the tool prioritises human review only |
| Macro context | Point-in-time pipeline is future work; it is not an input to frozen v01/v02 models |

## Development checks

```bash
npm run test:ui
python3 -m unittest tests.api.test_live_api tests.api.test_score_export_adapter
npm run build
```

## Repository map

```text
src/
├── common/               # provider-neutral utilities
├── fannie_mae/           # Fannie Mae research pipeline and reproducibility scripts
├── freddie_mac/          # Freddie Mac ingestion and preparation
└── prototype/            # React UI, FastAPI API, PostgreSQL audit trail

fannie_mae/               # configuration, restricted data layers, models, reports, bilingual documentation
freddie_mac/              # isolated future external-validation workflow
docs/assets/screenshots/  # versioned prototype screenshots
tests/                    # API and UI policy tests
```

## Documentation index

| Document | Description |
|---|---|
| [Russian dissertation chapters](fannie_mae/docs/docs_ru/chapters/) | Academic text, appendices, conclusions, and defence materials |
| [English dissertation chapters](fannie_mae/docs/docs_en/chapters/) | English chapter version and methodological appendices |
| [Methodological audit](fannie_mae/docs/docs_ru/appendices/appendix_a_methodological_audit.md) | Data, cleaning, leakage control, outcomes, splits, models, calibration, and triggers |
| [Data lineage and glossary](fannie_mae/docs/docs_ru/appendices/appendix_b_data_lineage_and_glossary.md) | Research layers, safe export, and terminology |
| [Final evidence audit](fannie_mae/reports/dissertation_finalization_v01/reference_audit_v01.md) | Numbering and local-link audit |

---

<div align="center"><strong>Explainable AI for credit-risk early warning</strong><br>Controlled research workflow for transparent expert review.</div>
