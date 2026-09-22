# SupTech research-prototype documentation

This directory records the design and implementation decisions for the
dissertation's browser-based research prototype.  The prototype visualises the
analytical workflow `data → score → alert → explanation → risk trigger →
expert review`.  It is not an automated credit, supervisory, or lending
decision system.

- `01_design_audit.md` records the supplied interface specification and its
  screen map.
- `02_react_compose_architecture.md` records the initial React and Docker
  Compose architecture.
- `09_data_contract_and_access_policy.md` records allowed alert fields and
  browser-access restrictions.
- `11_database_and_migrations.md` and `12_persistent_audit_workflow.md`
  record the PostgreSQL audit architecture.
- `13_safe_research_data_adapter.md` and
  `14_integration_testing_and_architecture.md` record the protected
  score-export boundary, UI/API integration and test procedure.
- `15_authentication_and_rbac.md` and `16_admin_api_and_role_governance.md`
  record local authentication, role-based access, user administration and the
  audit controls for access changes.
- `17_architecture_refactoring.md` records the safe alert contract and the
  frontend access-policy refactoring.
