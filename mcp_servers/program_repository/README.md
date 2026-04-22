# program_repository MCP Server

Query the per-customer production program backups under `customer_programs/`. Customer programs are **context, not canon** — this server is explicitly named and scoped so agents do not confuse them with authoritative dataset material.

## Install

```bash
pip install uv
uv pip install -e .
```

## Configure

| Var | Default | Purpose |
|-----|---------|---------|
| `CUSTOMER_PROGRAMS_PATH` | `../../customer_programs` | Path to `customer_programs/` directory |

## Tools

### `list_customers() -> list[dict]`

Return every customer + their systems.

### `get_program(customer_id: str, name: str, backup: str | None = None) -> dict`

Fetch the content of a `.src` / `.dat` / `.sub` file under a customer/system. `backup` optionally selects a specific dated backup directory; default is the most recent.

### `search(regex: str, scope: str | None = None, file_glob: str = "**/*.src") -> list[dict]`

ripgrep-like search within `customer_programs/`. `scope` may be a customer id or `customer_id/system`.

### `diff(path_a: str, path_b: str) -> dict`

Structural diff of two `.src` files: lines added / removed / modified, with a summary.

### `list_files(customer_id: str, system: str | None = None) -> list[str]`

Enumerate program files for a customer (optionally narrowed to a system).
