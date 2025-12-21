# Hydraulic Balancing Tool (hyd-abgleich)

A modern Django-based application to calculate optimal radiator valve settings for hydraulic balancing, improving heating efficiency and comfort in homes.

## Features

- **User Accounts:** Secure registration and login. Each user manages their own heating systems privately.
- **System Management:** Create and manage multiple heating systems (houses/apartments).
- **Step-by-Step Input:** Simple wizard-like interface to add rooms and radiators.
- **Hydraulic Calculation:** 
  - Estimates room heat demand based on area and insulation quality.
  - Calculates required flow rates (l/h) for radiators.
  - Suggests generic valve settings (1-6) based on target flow.
- **Modern UI:** Built with Bootstrap 5 and Django Crispy Forms for a clean, responsive experience.

## Project Structure

- `hyd_abgleich/`: Core Django settings and configuration.
- `hyd_balancing/`: Main application logic, including models, calculation engineering, and CRUD views.
- `users/`: Authentication app handling registration and user sessions.
- `manage.py`: Django management script.
- `pyproject.toml` / `uv.lock`: Dependency management via `uv`.

## Getting Started

### Prerequisites

- Python 3.11+
- `uv` (recommended) or `pip`

### Setup

1. **Clone and Install:**
   ```bash
   uv sync
   ```

2. **Environment Variables:**
   Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. **Database Setup:**
   ```bash
   uv run manage.py migrate
   ```

4. **Run Server:**
   ```bash
   uv run manage.py runserver
   ```
   Visit `http://127.0.0.1:8000` in your browser.

## How it Works

The calculation uses the formula:
`Flow (l/h) = Heat Load (W) / (1.163 * Delta T)`

- **Heat Load:** Estimated by multiplying room area by a specific demand factor (W/m²) determined by insulation quality (Poor: 150, Average: 100, Good: 50).
- **Delta T:** The temperature difference between supply and return water (e.g., 70/55 -> ΔT = 15K).

## License

This project is licensed under the MIT License.