# Project Context: hyd-abgleich

## Project Overview
**Name:** hyd-abgleich
**Purpose:** DIY Hydraulic balancing calculation tool for homeowners.
**Tech Stack:** Python 3.11, Django 5.2+, uv, Bootstrap 5, django-crispy-forms.

## Current Progress
- [x] Initial Django setup and `uv` integration.
- [x] Core Data Models (HeatingSystem, Room, Radiator).
- [x] CRUD Wizard for system input.
- [x] Engineering calculation logic (`calculation.py`).
- [x] User Authentication and Data Isolation (Users see only their own systems).
- [x] Functional "About" page.
- [ ] PDF Export of calculation results (Planned).
- [ ] Context7 MCP Server integration for AI-assisted building analysis.

## Project Structure
- `hyd_abgleich/`: Settings, URLs, WSGI/ASGI.
- `hyd_balancing/`: 
    - `models.py`: Heating entities and relationships.
    - `calculation.py`: The physics/engineering logic for flow rates.
    - `views.py`: CBVs for the wizard and calculations.
- `users/`: Registration and profile management.
- `.gemini/settings.json`: Configuration for MCP servers.

## Development Rules
- **Branching:** Use `feat/` for new features, `fix/` for bugs.
- **Security:** Ensure `LoginRequiredMixin` or `login_required` is used for all system-related views to prevent unauthorized access.
- **Validation:** Always validate room areas and temperatures to prevent division by zero in calculations.
- **Style:** Adhere to PEP 8. Use Crispy Forms for all form layouts.

## Running the App
```bash
uv run manage.py migrate
uv run manage.py runserver
```

## Context7 Integration (Experimental)
The project includes a `context7` MCP server entry point via `manage.py run_context7_server`. This allows AI assistants to interact with the building data directly when configured in their environment.
