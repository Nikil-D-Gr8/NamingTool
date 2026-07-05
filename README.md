# NamingTool

A modern, Django-based internal tool for generating, tracking, and managing canonical resource identities across your infrastructure.

NamingTool helps enforce a consistent naming convention:
`<owner>-<provider>-<environment>-<resource-type>-<purpose>-<instance>`
*(e.g., `ops-aws-prd-vm-web-001`)*

## Features

- **Canonical Naming:** Enforces strict naming conventions for infrastructure resources.
- **Resource Groups:** Organize related resources logically (e.g., "Core Network", "Blog Stack").
- **Dynamic Vocabulary:** Dropdown options are fully configurable via a `vocabulary.yaml` file, editable directly from the UI.
- **Auto-Instance Detection:** Automatically detects and suggests the next available instance number for a given configuration.
- **Tagging & Metadata:** Add key-value tags and rich notes to any resource.

## Installation & Setup

1. **Clone the repository and enter the directory:**
   ```bash
   git clone <repo-url>
   cd NamingTool
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create an admin user:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   Access the application at `http://localhost:8000/` and log in with your superuser credentials.

## Usage Guide

### 1. Dashboard
The dashboard provides a high-level overview of your tracked resources, breakdown by environment and resource type, and quick access to recently created resources.

### 2. Managing Vocabulary
Navigate to **Vocabulary** in the sidebar. This allows you to define the available options for:
- Owners (e.g., `ops`, `dev`)
- Providers (e.g., `aws`, `hom`)
- Environments (e.g., `prd`, `dev`)
- Resource Types (e.g., `vm`, `net`)
- Purposes (e.g., `db`, `web`)

These values populate the dropdowns when creating a new resource. *(Note: You can also use the "✏️ Custom…" option while creating a resource if you need an on-the-fly value).*

### 3. Resource Groups
Navigate to **Groups** to create logical collections for your resources.
- Create a group (e.g., "Database Cluster").
- Assign a custom color to the group for easy visual identification.

### 4. Creating Resources
Navigate to **Create**.
1. Select a **Resource Group**.
2. Pick your identity fields (Owner, Provider, Environment, Resource Type, Purpose).
3. Click the **Auto** button next to the Instance field to automatically fetch the next available number (e.g., `001`, `002`).
4. (Optional) Add key-value tags and notes.
5. The canonical name is automatically previewed at the top. Click **Create Resource** to save.

## Tech Stack
- **Backend:** Django (Python)
- **Database:** SQLite (default)
- **Frontend:** HTML, Vanilla JS, Custom CSS (Glassmorphism design)
