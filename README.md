# freddie-mac-loan-level-early-warning-dataset

## SupTech-inspired research prototype

The local research prototype combines a React interface, FastAPI service and
PostgreSQL audit database. It uses synthetic alerts by default; raw Fannie Mae
data never enters the browser client.

```bash
docker compose up --build
```

- UI: `http://localhost:5173`
- API documentation: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

See [SupTech documentation](docs/suptech/README.md) for the data contract,
adapter boundary, audit workflow and dissertation architecture.

The repository keeps provider-specific work fully separated:

- `freddie_mac/` — the original Freddie Mac work, sources, pipeline and bilingual documentation.
- `fannie_mae/` — the active Fannie Mae Primary Dataset work, sources, pipeline and bilingual documentation.
- `src/` — the shared source-code root: provider-specific scripts are located in
  `src/fannie_mae/` and `src/freddie_mac/`; reusable provider-neutral code is
  reserved for `src/common/`.

The datasets must never be combined into one training table. The active dataset
is Fannie Mae; Freddie Mac remains preserved as a separate implementation.

The future SupTech application will use `src/prototype/` for its services and
data-access layer. It will consume documented alerts and audit records rather
than directly combining the two providers' raw loan-level datasets.
