# Customer Program Repository Index

Customer-organized index of production KUKA programs stored in this workspace.

---

## Customers

| ID | Business Name | Systems | Active |
|----|--------------|---------|--------|
| `_example_customer` | Example Customer (placeholder) | 1 | no |

---

## Systems Overview

| Customer | System | Application | Robot | Controller | Fieldbus | Collaborative |
|----------|--------|-------------|-------|------------|----------|---------------|
| `_example_customer` | `example_cell` | pick_place | KR 16 R2010 | KR C5 | Profinet | no |

---

## How Customers Are Organized

```
customer_programs/
├─ PROGRAM_REPOSITORY_INDEX.md  (this file)
├─ _manifest.json               (machine-readable version)
├─ _manifest.schema.json
├─ <customer_id>/
│  ├─ README.md                 (customer overview, history, contacts)
│  ├─ _manifest.json            (customer-level manifest)
│  ├─ <system_id>/
│  │  ├─ README.md              (system overview)
│  │  ├─ YYYY-MM-DD_backup/     (timestamped program backups)
│  │  │  ├─ <program>.src
│  │  │  └─ <data>.dat
│  │  └─ tasks/
│  │     └─ YYYY-MM-DD_<slug>/  (in-progress task directories)
│  │        └─ task_state.json
│  └─ ...
└─ _example_customer/           (template; keep in place)
```

---

## Usage

- **Read-only reference.** Customer programs are production backups. Read for context, NEVER treat as a syntax authority.
- **MCP retrieval.** Use `program_repository.list_customers()`, `program_repository.get_program(customer_id, name)`, `program_repository.search(regex, scope)`.
- **Onboard a new customer** via `cowork/workflows/customer_onboarding.md`.
- **Review / audit** via `cowork/workflows/code_review.md`.

---

## Rules

- Do NOT copy customer patterns into the normalized dataset — they are context, not canon.
- Do NOT edit a customer program without a `HANDOFF_*.md` and matching `REVIEW_*.md`.
- Do NOT delete old backups; they are the only record of what ran when.
- Commit customer directory updates separately from workspace infrastructure updates.
