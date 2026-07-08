# NamingTool

A **pure static** resource naming tool for infrastructure. Generate canonical names and build tags — then copy & paste them into NetBox or wherever you need them.

**No server required.** Just open `index.html` in your browser.

## Features

- **Name Generator** — pick owner, provider, environment, resource type, purpose, and instance number to build a canonical name like `nik-hom-prd-vm-core-001`
- **Tags Builder** — add key:value tags and export them as plain text, JSON, YAML, or CSV
- **Vocabulary Browser** — view and extend the dropdown options (additions persist in localStorage)
- **Copy History** — recently copied names are remembered across sessions
- **Custom Entries** — select "✏️ Custom…" in any dropdown to type a freeform value

## Usage

```bash
# Option A: just open the file
xdg-open index.html        # Linux
open index.html             # macOS

# Option B: serve it (for clipboard API over HTTP)
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Structure

```
NamingTool/
├── index.html      # Single-page app (Generator + Vocabulary)
├── css/
│   └── style.css   # Design system (dark mode, glassmorphism)
├── js/
│   └── app.js      # All logic + embedded vocabulary data
├── LICENSE
└── README.md
```

## Customising the Vocabulary

Edit the `DEFAULT_VOCAB` object at the top of `js/app.js`, or use the **Vocabulary** page in the app to add entries at runtime (saved in localStorage).

## License

MIT
