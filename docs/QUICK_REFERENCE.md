# ACAD=GIS Quick Reference Card

**For rapid tool development and maintenance**

## 🚀 Tool Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ACAD=GIS - Tool Name</title>
    
    <!-- React -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Shared Styles -->
    <link rel="stylesheet" href="../shared/styles.css">
</head>
<body class="grid-background">
    <div id="root"></div>

    <!-- Shared Components -->
    <script src="../shared/components.js"></script>

    <script type="text/babel">
        const { useState, useEffect } = React;

        function ToolName() {
            const [data, setData] = useState([]);
            const [loading, setLoading] = useState(true);

            useEffect(() => {
                loadData();
            }, []);

            const loadData = async () => {
                setLoading(true);
                try {
                    const result = await api.get('/endpoint');
                    setData(result);
                } catch (error) {
                    console.error('Failed to load:', error);
                    ToastManager.error('Failed to load data');
                }
                setLoading(false);
            };

            return (
                <div className="page-wrapper">
                    <Header 
                        title="Tool Name"
                        subtitle="Tool Description"
                        showBackButton={true}
                    />

                    <main className="main-content">
                        <div className="container">
                            {loading ? (
                                <LoadingSpinner text="Loading..." />
                            ) : (
                                <div>
                                    {/* Your content here */}
                                </div>
                            )}
                        </div>
                    </main>

                    <Footer />
                </div>
            );
        }

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<ToolName />);
    </script>
</body>
</html>
```

## 🎨 CSS Classes Quick Reference

### Layout
```html
<div class="page-wrapper">              <!-- Full page container -->
<div class="container">                 <!-- Centered content area -->
<div class="main-content">              <!-- Main content section -->
<div class="grid grid-cols-3">         <!-- 3-column grid -->
```

### Cards
```html
<div class="card">                      <!-- Basic card -->
<div class="card-header">               <!-- Card header section -->
<h3 class="card-title">Title</h3>       <!-- Card title -->
<div class="card-body">                 <!-- Card body -->
<div class="card-footer">               <!-- Card footer -->
```

### Buttons
```html
<button class="btn btn-primary">        <!-- Primary action -->
<button class="btn btn-secondary">      <!-- Secondary action -->
<button class="btn btn-success">        <!-- Success/confirm -->
<button class="btn btn-danger">         <!-- Danger/delete -->
<button class="btn btn-ghost">          <!-- Subtle/ghost -->
<button class="btn btn-icon">           <!-- Icon only (40x40) -->
```

### Forms
```html
<div class="form-group">
    <label class="form-label">Label</label>
    <input class="form-input" type="text">
</div>

<textarea class="form-textarea"></textarea>
<select class="form-select"></select>
<input type="checkbox" class="form-checkbox">
```

### Alerts
```html
<div class="alert alert-success">       <!-- Success message -->
<div class="alert alert-error">         <!-- Error message -->
<div class="alert alert-warning">       <!-- Warning message -->
<div class="alert alert-info">          <!-- Info message -->
```

### Utilities
```html
<div class="flex">                      <!-- Flexbox container -->
<div class="flex-col">                  <!-- Flex column -->
<div class="items-center">              <!-- Align items center -->
<div class="justify-between">           <!-- Space between -->
<div class="gap-md">                    <!-- Medium gap -->
<div class="text-center">               <!-- Center text -->
<div class="hidden">                    <!-- Hide element -->
```

## 🧩 Component Quick Reference

### API Status
```jsx
<ApiStatus />
```
Shows green/red indicator for API connection.

### Loading Spinner
```jsx
<LoadingSpinner text="Loading data..." />
```

### Alert
```jsx
<Alert 
    type="success"              // success, error, warning, info
    message="Operation successful!"
    onClose={() => {}}          // Optional close handler
/>
```

### Modal
```jsx
<Modal
    isOpen={showModal}
    onClose={() => setShowModal(false)}
    title="Modal Title"
    size="medium"               // small, medium, large
    footer={
        <>
            <button className="btn btn-ghost" onClick={handleClose}>Cancel</button>
            <button className="btn btn-primary" onClick={handleSave}>Save</button>
        </>
    }
>
    <p>Modal content here</p>
</Modal>
```

### Confirm Dialog
```jsx
<ConfirmDialog
    isOpen={showConfirm}
    onClose={() => setShowConfirm(false)}
    onConfirm={handleDelete}
    title="Confirm Delete"
    message="Are you sure you want to delete this item?"
    confirmText="Delete"
    cancelText="Cancel"
    danger={true}               // Use red button
/>
```

### Empty State
```jsx
<EmptyState
    icon="folder-open"
    title="No Projects Found"
    message="Create your first project to get started"
    action={
        <button className="btn btn-primary" onClick={handleCreate}>
            <i className="fas fa-plus"></i>
            Create Project
        </button>
    }
/>
```

### Stat Card
```jsx
<StatCard
    icon="folder"
    label="Total Projects"
    value={42}
    color="blue"                // blue, green, orange, purple, red
/>
```

### Header
```jsx
<Header
    title="Tool Name"
    subtitle="Tool description"
    showBackButton={true}
    backUrl="../tool_launcher.html"
    rightContent={<button>Action</button>}
/>
```

### Search Bar
```jsx
<SearchBar
    placeholder="Search projects..."
    value={searchTerm}
    onChange={setSearchTerm}
    onClear={() => setSearchTerm('')}
/>
```

### Badge
```jsx
<Badge color="blue" icon="check">Active</Badge>
<Badge color="green" icon="globe">GIS</Badge>
<Badge color="gray">Draft</Badge>
```

## 🔌 API Helper Quick Reference

### GET Request
```javascript
const data = await api.get('/projects');
const single = await api.get('/projects/abc-123');
```

### POST Request
```javascript
const result = await api.post('/projects', {
    project_name: 'New Project',
    client_name: 'Client Name'
});
```

### PUT Request
```javascript
const result = await api.put('/projects/abc-123', {
    project_name: 'Updated Name'
});
```

### DELETE Request
```javascript
const result = await api.delete('/projects/abc-123');
```

### File Upload
```javascript
const formData = new FormData();
formData.append('file', fileObject);
formData.append('project_id', projectId);
const result = await api.upload('/import/dxf', formData);
```

### Health Check
```javascript
const isConnected = await api.checkHealth();
```

### Error Handling
```javascript
try {
    const data = await api.get('/projects');
} catch (error) {
    console.error('API Error:', error);
    ToastManager.error('Failed to load projects');
}
```

## 💬 Toast Notifications

```javascript
ToastManager.success('Project created!');
ToastManager.error('Failed to save project');
ToastManager.warning('Please fill all fields');
ToastManager.info('Processing...');

// With custom duration (default 3000ms)
ToastManager.success('Saved!', 5000);

// No auto-dismiss
ToastManager.error('Critical error', 0);
```

## 🛠️ Utility Functions

### Format Date
```javascript
const formatted = formatDate('2025-01-19T10:30:00Z');
// Output: "Jan 19, 2025, 10:30 AM"
```

### Debounce (for search inputs)
```javascript
const debouncedSearch = debounce((term) => {
    performSearch(term);
}, 300);
```

### Copy to Clipboard
```javascript
await copyToClipboard('Text to copy');
// Shows success toast automatically
```

### Download File
```javascript
downloadFile(
    'File content',
    'filename.txt',
    'text/plain'
);
```

## 🎨 Color Variables

```css
var(--color-bg-primary)        /* #0a0e27 - Main background */
var(--color-bg-secondary)      /* #1e293b - Secondary background */
var(--color-text-primary)      /* #e0e7ff - Main text */
var(--color-text-secondary)    /* #94a3b8 - Secondary text */
var(--color-accent-blue)       /* #3b82f6 - Primary accent */
var(--color-accent-green)      /* #10b981 - Success */
var(--color-accent-red)        /* #ef4444 - Error */
var(--color-accent-orange)     /* #f59e0b - Warning */
```

## 📏 Spacing Scale

```css
var(--spacing-xs)              /* 4px */
var(--spacing-sm)              /* 8px */
var(--spacing-md)              /* 16px */
var(--spacing-lg)              /* 24px */
var(--spacing-xl)              /* 32px */
```

## 🎯 Common Patterns

### CRUD List Component
```jsx
function ItemList() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingItem, setEditingItem] = useState(null);

    const loadItems = async () => {
        setLoading(true);
        try {
            const data = await api.get('/items');
            setItems(data);
        } catch (error) {
            ToastManager.error('Failed to load items');
        }
        setLoading(false);
    };

    const handleCreate = () => {
        setEditingItem(null);
        setShowModal(true);
    };

    const handleEdit = (item) => {
        setEditingItem(item);
        setShowModal(true);
    };

    const handleSave = async (formData) => {
        try {
            if (editingItem) {
                await api.put(`/items/${editingItem.id}`, formData);
                ToastManager.success('Item updated!');
            } else {
                await api.post('/items', formData);
                ToastManager.success('Item created!');
            }
            setShowModal(false);
            loadItems();
        } catch (error) {
            ToastManager.error('Failed to save item');
        }
    };

    const handleDelete = async (itemId) => {
        try {
            await api.delete(`/items/${itemId}`);
            ToastManager.success('Item deleted!');
            loadItems();
        } catch (error) {
            ToastManager.error('Failed to delete item');
        }
    };

    useEffect(() => {
        loadItems();
    }, []);

    return (
        <div className="page-wrapper">
            <Header title="Items" showBackButton />
            <main className="main-content">
                <div className="container">
                    <div className="flex justify-between items-center mb-lg">
                        <h2>Item List</h2>
                        <button className="btn btn-primary" onClick={handleCreate}>
                            <i className="fas fa-plus"></i>
                            Create Item
                        </button>
                    </div>

                    {loading ? (
                        <LoadingSpinner />
                    ) : items.length === 0 ? (
                        <EmptyState
                            icon="inbox"
                            title="No Items"
                            message="Get started by creating your first item"
                            action={
                                <button className="btn btn-primary" onClick={handleCreate}>
                                    Create Item
                                </button>
                            }
                        />
                    ) : (
                        <div className="grid grid-cols-3">
                            {items.map(item => (
                                <div key={item.id} className="card">
                                    <h3>{item.name}</h3>
                                    <p>{item.description}</p>
                                    <div className="flex gap-sm mt-md">
                                        <button className="btn btn-secondary" onClick={() => handleEdit(item)}>
                                            Edit
                                        </button>
                                        <button className="btn btn-danger" onClick={() => handleDelete(item.id)}>
                                            Delete
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </main>
            <Footer />

            {/* Create/Edit Modal */}
            <Modal isOpen={showModal} onClose={() => setShowModal(false)} title={editingItem ? 'Edit Item' : 'Create Item'}>
                {/* Form content here */}
            </Modal>
        </div>
    );
}
```

### Search with Debounce
```jsx
function SearchableList() {
    const [items, setItems] = useState([]);
    const [filteredItems, setFilteredItems] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');

    const performSearch = (term) => {
        if (!term) {
            setFilteredItems(items);
            return;
        }
        const filtered = items.filter(item =>
            item.name.toLowerCase().includes(term.toLowerCase())
        );
        setFilteredItems(filtered);
    };

    const debouncedSearch = debounce(performSearch, 300);

    useEffect(() => {
        debouncedSearch(searchTerm);
    }, [searchTerm]);

    return (
        <div>
            <SearchBar
                value={searchTerm}
                onChange={setSearchTerm}
                onClear={() => setSearchTerm('')}
            />
            {/* Render filteredItems */}
        </div>
    );
}
```

## 📝 API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Check API status |
| GET | `/api/stats` | System statistics |
| GET | `/api/projects` | List projects |
| GET | `/api/projects/{id}` | Get project |
| POST | `/api/projects` | Create project |
| PUT | `/api/projects/{id}` | Update project |
| DELETE | `/api/projects/{id}` | Delete project |
| GET | `/api/drawings` | List drawings |
| GET | `/api/drawings/{id}` | Get drawing |
| GET | `/api/drawings/{id}/render` | Drawing render data |
| POST | `/api/drawings` | Create drawing |
| PUT | `/api/drawings/{id}` | Update drawing |
| DELETE | `/api/drawings/{id}` | Delete drawing |
| POST | `/api/import/dxf` | Upload DXF file |

## 🐛 Debugging Tips

### Check API Connection
```javascript
console.log('API URL:', API_BASE_URL);
const health = await api.checkHealth();
console.log('API Connected:', health);
```

### Log API Responses
```javascript
const data = await api.get('/projects');
console.log('Received data:', data);
console.table(data); // Pretty table view
```

### React DevTools
1. Install React DevTools extension
2. Press F12 → Components tab
3. View component state and props

### Network Tab
1. Press F12 → Network tab
2. Filter by XHR/Fetch
3. Click request → Preview/Response
4. Check status codes (200 = success, 500 = server error)

## 🚀 Performance Tips

1. **Limit data fetching**
   ```javascript
   const data = await api.get('/drawings?limit=100');
   ```

2. **Use loading states**
   ```javascript
   if (loading) return <LoadingSpinner />;
   ```

3. **Debounce search inputs**
   ```javascript
   const debouncedSearch = debounce(search, 300);
   ```

4. **Memoize expensive calculations**
   ```javascript
   const filtered = useMemo(() => 
       items.filter(i => i.active),
       [items]
   );
   ```

## ✅ Pre-Deploy Checklist

- [ ] No console errors
- [ ] API connection works
- [ ] CRUD operations tested
- [ ] Loading states display
- [ ] Error messages show correctly
- [ ] Modals open and close
- [ ] Search/filter works
- [ ] Responsive on mobile
- [ ] Icons load correctly
- [ ] Shared styles imported
- [ ] Shared components imported
- [ ] Back button works

---

**Keep this handy while building tools!** 📌
