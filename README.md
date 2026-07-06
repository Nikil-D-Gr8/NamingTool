# NamingTool

A stateless, YAML-driven resource naming and tag-building utility. Designed to complement [NetBox](https://netbox.dev/) — generate canonical names and copy-paste tags effortlessly.

## Naming Convention

```
<owner>-<provider>-<environment>-<resource_type>-<purpose>-<instance>
```

*Example:* `nik-hom-prd-vm-core-001`

## Features

- **Name Generator** — Pick identity fields from dropdowns, see the canonical name in real time, and copy it to your clipboard.
- **Tags Builder** — Add key:value tags and export them as `key: value`, JSON, YAML, or CSV for pasting into NetBox.
- **Dynamic Vocabulary** — All dropdown options are driven by `naming/vocabulary.yaml`. Edit the file or use the in-app Vocabulary page — no migrations, no restarts.
- **Name History** — Recently copied names are saved in your browser's `localStorage` for quick reference.
- **Fully Stateless** — No authentication, no server-side state. Just a utility you run locally.

## Quick Start

```bash
# Clone and enter the directory
git clone https://github.com/Nikil-D-Gr8/NamingTool.git
cd NamingTool

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run the dev server
python manage.py runserver
```

Open [http://localhost:8000/](http://localhost:8000/) and start generating names.

## Development

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov
```

### Linting & Formatting

```bash
ruff check .
ruff format .
```

### Type Checking

```bash
mypy naming/
```

## Project Structure

```
NamingTool/
├── config/              # Django project settings & URL root
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── naming/              # Main Django app
│   ├── apps.py
│   ├── urls.py
│   ├── views.py         # home + vocabulary_manage
│   ├── vocab.py         # YAML loader & choice builders
│   ├── vocabulary.yaml  # All dropdown data (edit freely)
│   ├── templatetags/
│   │   └── naming_tags.py
│   ├── templates/naming/
│   │   ├── base.html
│   │   ├── home.html
│   │   └── vocabulary.html
│   └── static/naming/
│       ├── css/style.css
│       └── js/app.js
├── tests/               # pytest test suite
│   ├── conftest.py
│   ├── fixtures/
│   │   └── test_vocabulary.yaml
│   ├── test_vocab.py
│   ├── test_views.py
│   ├── test_urls.py
│   ├── test_templatetags.py
│   └── test_app.py
├── pyproject.toml       # Project metadata, deps, tool configs
├── requirements.txt     # Pinned runtime deps (for simple installs)
├── manage.py
├── LICENSE
└── README.md
```

## Tech Stack

- **Backend:** Django 6 (Python 3.11+)
- **Frontend:** HTML, Vanilla JS, Custom CSS (dark mode, glassmorphism)
- **Data:** YAML
- **Testing:** pytest + pytest-django + pytest-cov
- **Linting:** Ruff
- **Types:** mypy + django-stubs

## License

MIT — see [LICENSE](LICENSE).
