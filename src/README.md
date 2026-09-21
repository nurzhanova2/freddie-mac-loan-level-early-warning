# Shared project source code

`src/` is the common code root for both empirical workstreams and the future
SupTech prototype.

```text
src/
├── common/       # shared utilities; provider-neutral only
├── fannie_mae/   # Fannie Mae ingestion, panels, outcomes, models, and audits
├── freddie_mac/  # Freddie Mac ingestion, panels, and validation
└── prototype/    # future SupTech application services and database access
```

Provider-specific scripts must remain in their respective directories. Shared
code may not assume field names, status codes, or outcome definitions from only
one provider.
