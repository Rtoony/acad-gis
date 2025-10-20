# ACAD-GIS Component Library

Last Updated: October 2025

The UI is intentionally thin. Components exist to speed up tool scaffolding, not to be a design system.

## Using shared components
```html
<!-- Required dependencies -->
<script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
<script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

<!-- ACAD-GIS shared -->
<link rel="stylesheet" href="../shared/styles.css">
<script src="../shared/components.js"></script>
<script src="../shared/react-components.js"></script>
```

Components are exposed on `window.*` (e.g., `window.DataTable`, `window.Modal`, `window.Header`).

## DataTable (summary)
- Props: `data`, `columns`, `searchable`, `pagination`, `pageSize`, `onView/onEdit/onDelete`
- Column: `{ key, label, sortable?, format?, render? }`

Minimal example:
```js
const columns = [
  { key: 'name', label: 'Name', sortable: true },
  { key: 'created_at', label: 'Created', format: 'date' }
];
const rows = [{ name: 'Project A', created_at: '2025-01-01' }];
React.createElement(window.DataTable, { data: rows, columns });
```

## Modal / Header / Badge
- `window.Modal({ isOpen, onClose, title, footer, size })`
- `window.Header({ title, subtitle })`
- `window.Badge({ color, children })`

## Notes
- Prefer embedding simple logic in each tool and using these components only as helpers.

