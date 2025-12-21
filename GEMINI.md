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

## Development

### Prerequisites
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