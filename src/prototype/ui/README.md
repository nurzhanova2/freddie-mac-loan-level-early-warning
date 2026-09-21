# SupTech React UI

The browser interface for the dissertation's SupTech-inspired research
prototype. Start it from the repository root:

```bash
docker compose up --build
```

Open `http://localhost:5173`. The UI communicates only with the controlled
API alert DTO; it never receives raw Fannie Mae files, stable loan identifiers,
or training samples. The Compose stack includes a local PostgreSQL database
for demo accounts and audit events, not an automated lending or supervisory
decision system.
