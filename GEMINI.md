# Project Context: hyd-abgleich

## Project Overview
**Name:** hyd-abgleich
**Purpose:** Hydraulic balancing calculation system (inferred).
**Tech Stack:** Python, Django, uv (package manager).

## Project Structure
- `hyd_abgleich/`: Django project configuration and settings.
- `manage.py`: Django's command-line utility.
- `pyproject.toml`: Python project configuration and dependencies (managed by `uv`).
- `uv.lock`: Dependency lock file.

## Development Rules
- **Branching Strategy:** Always create a new branch for every new feature, bug fix, or significant step in development. Use descriptive branch names (e.g., `feature/add-models`, `fix/issue-description`).
- **Best Practices:** Strictly adhere to Python (PEP 8) and Django best practices. This includes proper directory structure, use of Django models/forms, DRY principle, and maintainable code patterns.

## Prerequisites
- `uv` installed.

### Setup
1.  **Install Dependencies:**
    ```bash
    uv sync
    ```

### Running the Server
To start the Django development server:
```bash
uv run manage.py runserver
```

### Management
Run standard Django commands using `uv run manage.py <command>`.
Example:
```bash
uv run manage.py migrate
uv run manage.py startapp myapp
```