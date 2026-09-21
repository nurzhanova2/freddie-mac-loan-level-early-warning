# SupTech prototype application code

The application consists of:

- `ui/` — React browser client;
- `api/` — FastAPI boundary for synthetic demo alerts and future approved
  server-side adapters.

Database access, persistent audit trail and real-data adapters are subsequent
implementation stages. Every service must use published data contracts rather
than directly read raw loan-level archives.
