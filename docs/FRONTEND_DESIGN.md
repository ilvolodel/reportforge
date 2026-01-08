# 🎨 Frontend Design - ReportForge

## Tinexta InfoCert Branding

### Colori Ufficiali

```css
:root {
    --infocert-blue: #0072CE;           /* Colore principale InfoCert */
    --infocert-dark-blue: #005a9e;      /* Hover/Active states */
    --infocert-light-blue: #e6f3fb;     /* Backgrounds */
    --infocert-gray: #4a5568;           /* Text secondary */
    --infocert-light-gray: #f7f9fc;     /* Page background */
    --success-green: #10b981;           /* Success messages */
    --warning-orange: #f59e0b;          /* Warnings */
    --error-red: #ef4444;               /* Errors */
}
```

### Sorgente

Colori estratti direttamente dai loghi ufficiali InfoCert:
- **Logo Legalmail SVG**: `fill="#0072CE"` (blu principale)
- **Website**: https://www.infocert.it

---

## 🖼️ Layout Structure

### Login Page (`/frontend/templates/login.html`)

**Status**: ✅ Completato

**Features**:
- Gradient background con colori InfoCert
- Logo SVG personalizzato
- Magic Link authentication form
- AJAX submission con feedback
- Loading states
- Success/Error alerts
- Responsive design

**Screenshot descrizione**:
```
┌─────────────────────────────────────┐
│     Blu InfoCert Gradient BG        │
│                                     │
│   ┌───────────────────────────┐   │
│   │   📊 ReportForge          │   │
│   │   by Tinexta InfoCert     │   │
│   │                           │   │
│   │   [Email input]           │   │
│   │                           │   │
│   │   [Send Magic Link]       │   │
│   │                           │   │
│   │   🔐 Passwordless...      │   │
│   └───────────────────────────┘   │
└─────────────────────────────────────┘
```

---

### Dashboard Page (`/frontend/templates/dashboard.html`)

**Status**: ✅ Layout completato (dati statici)

**Structure**:

```
┌──────────────────────────────────────────────────────┐
│  Sidebar (260px)       │     Main Content            │
│                        │                             │
│  📊 ReportForge        │  Welcome back! 👋           │
│  Tinexta InfoCert      │  [+ New Report] [Gen PDF]  │
│                        │                             │
│  📈 Dashboard (active) │  ┌─────┐ ┌─────┐ ┌─────┐  │
│                        │  │ 12  │ │  8  │ │2.6M€│  │
│  📄 Reports            │  │Reps │ │Proj │ │Rev. │  │
│  🚀 Projects           │  └─────┘ └─────┘ └─────┘  │
│  👥 Clients            │                             │
│  💰 Revenue & Saving   │  Quick Actions:             │
│  👨‍💼 Team Members       │  [Create] [Add] [Import]   │
│                        │                             │
│  📥 Import Data        │                             │
│  ⚙️ Settings           │                             │
│                        │                             │
│  ─────────────────────│                             │
│  [👤 User Info] [🚪]  │                             │
└──────────────────────────────────────────────────────┘
```

**Components**:

1. **Sidebar** (260px fixed width)
   - Logo + branding
   - Navigation menu con icons
   - Sezioni: Data Management, Tools
   - User menu fisso in basso

2. **Main Content Area**
   - Header con titolo + azioni
   - Stats cards (4 cards grid)
   - Quick actions (4 cards grid)

3. **Navigation Items**:
   - 📈 Dashboard
   - 📄 Reports
   - 🚀 Projects
   - 👥 Clients
   - 💰 Revenue & Saving
   - 👨‍💼 Team Members
   - 📥 Import Data
   - ⚙️ Settings

---

## 🎨 Design Patterns

### Buttons

```css
/* Primary Button (InfoCert Blue) */
.btn-primary {
    background: #0072CE;
    color: white;
    border-radius: 8px;
    padding: 0.75rem 1.5rem;
}

.btn-primary:hover {
    background: #005a9e;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 114, 206, 0.3);
}

/* Secondary Button */
.btn-secondary {
    background: white;
    color: #0072CE;
    border: 2px solid #0072CE;
}
```

### Cards

```css
.card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: all 0.2s;
}

.card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}
```

### Inputs

```css
input:focus {
    outline: none;
    border-color: #0072CE;
    box-shadow: 0 0 0 3px rgba(0, 114, 206, 0.1);
}
```

---

## 📱 Responsive Design

### Breakpoints

```css
/* Mobile: < 768px */
@media (max-width: 767px) {
    .sidebar {
        display: none; /* Mobile menu toggle needed */
    }
    
    .main-content {
        margin-left: 0;
    }
    
    .cards-grid {
        grid-template-columns: 1fr;
    }
}

/* Tablet: 768px - 1024px */
@media (min-width: 768px) and (max-width: 1024px) {
    .cards-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

/* Desktop: > 1024px */
@media (min-width: 1024px) {
    .cards-grid {
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    }
}
```

---

## 🚀 Prossimi Passi Frontend

### 1. ⏳ Pages da creare

Seguendo lo stesso design pattern:

- **Reports List** (`/reports`)
  - Tabella con filtri
  - Search bar
  - Paginazione
  - Actions: View, Edit, Delete, Generate PDF

- **Report Form** (`/reports/new`, `/reports/:id/edit`)
  - Multi-step form
  - Executive Summary section
  - Projects section
  - Sales/Revenue section
  - Preview before save

- **Projects List** (`/projects`)
  - Cards grid
  - Filter by category
  - Status indicators

- **Projects Form** (`/projects/new`, `/projects/:id/edit`)
  - Nome, categoria, descrizione
  - Stakeholders multi-select
  - Status, dates

- **Clients List** (`/clients`)
  - Table view
  - Quick filters (tipo cliente)
  - Search

- **Clients Form** (`/clients/new`, `/clients/:id/edit`)
  - Info cliente
  - Contact details
  - Logo upload (opzionale)

- **Revenue & Saving** (`/revenue`)
  - Tabs: 2025 / 2026
  - Subscriptions vs One-time
  - Charts/Graphs

- **Team Members** (`/team`)
  - Cards grid
  - Roles
  - Add/Edit/Remove

- **Import Data** (`/import`)
  - File upload (CSV, Excel, PPTX)
  - Preview before import
  - Mapping columns

- **Settings** (`/settings`)
  - User preferences
  - Email configuration
  - Template customization

### 2. ⏳ Components da creare

Riusabili tra le varie pagine:

```
/frontend/templates/components/
├── header.html
├── sidebar.html
├── footer.html
├── card.html
├── table.html
├── form_input.html
├── modal.html
├── alert.html
└── pagination.html
```

### 3. ⏳ JavaScript (Alpine.js o Vanilla)

**Funzionalità da implementare**:
- Form validation
- AJAX CRUD operations
- Modal dialogs
- Toast notifications
- Data tables (sorting, filtering)
- Charts (optional - Chart.js)

**Esempio Alpine.js integration**:

```html
<script src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>

<div x-data="{ open: false }">
    <button @click="open = true">Open Modal</button>
    
    <div x-show="open" @click.away="open = false">
        <!-- Modal content -->
    </div>
</div>
```

---

## 📦 Assets Structure

```
/frontend/
├── static/
│   ├── css/
│   │   ├── infocert.css       (main stylesheet)
│   │   └── components.css     (reusable components)
│   ├── js/
│   │   ├── app.js             (main JS)
│   │   ├── api.js             (API calls)
│   │   └── utils.js           (helpers)
│   └── assets/
│       ├── logo-infocert.svg
│       └── icons/
└── templates/
    ├── base.html              (base template con sidebar)
    ├── login.html             ✅ Done
    ├── dashboard.html         ✅ Done
    ├── reports/
    │   ├── list.html
    │   ├── form.html
    │   └── view.html
    ├── projects/
    │   ├── list.html
    │   └── form.html
    ├── clients/
    │   ├── list.html
    │   └── form.html
    ├── revenue/
    │   └── list.html
    ├── team/
    │   └── list.html
    ├── import/
    │   └── upload.html
    ├── settings/
    │   └── index.html
    └── components/
        ├── header.html
        ├── sidebar.html
        └── ...
```

---

## 🎯 Design Principles

1. **Consistency**: Tutti gli elementi seguono lo stesso design pattern
2. **InfoCert Branding**: Colori e stile ufficiali
3. **Responsive**: Mobile-first approach
4. **Accessibility**: ARIA labels, contrasto colori
5. **Performance**: CSS inline per critical path, lazy load JS
6. **UX**: Feedback immediato, loading states, error handling

---

## 🔗 References

- **InfoCert Website**: https://www.infocert.it
- **Color Palette**: SVG logos at `https://img.infocert.it/loghi-tinexta-infocert/`
- **Tinexta Group**: https://www.tinexta.com (note: website currently offline)

---

**Last Updated**: 2026-01-08
**Status**: Login + Dashboard completati, CRUD pages da implementare
