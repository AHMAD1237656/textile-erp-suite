TechImport Enterprise ERP Suite — Extended EditionNext-Generation Multi-Branch Enterprise Resource Planning & Supply Chain PlatformLead Architect & Original Design: Muhammad DanishExtended Engineering & Portfolio Implementations: Muhammad Ahmad📌 Executive SummaryTechImport Enterprise ERP is a modular, high-performance web enterprise resource planning suite engineered specifically for import houses, wholesale distributors, textile conglomerates, and manufacturing entities. It bridges the gap between fast-paced supply chain operations and financial ledger accuracy.Architected initially by Muhammad Danish and extended into a portfolio showcase by Muhammad Ahmad, the platform delivers real-time visibility into multi-branch inventory, automates procurement-to-payment and order-to-cash pipelines, features automated double-entry ledger bookkeeping, and integrates modern warehouse utilities such as in-memory QR labeling and active low-stock monitoring.🏛️ System ArchitectureTechImport ERP is built on a decoupled, domain-driven Django architecture. Each business function lives within its own isolated Django application while communicating seamlessly through standardized models, signals, and shared core utilities.1. High-Level Architectural Flowchart┌────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER (UI/UX)                      │
│   Django Templates (DTL) • Bootstrap 5.3 • Tailwind CSS (tw-*)         │
│   Chart.js • Tabulator/DataTables • Select2 • Flatpickr • SweetAlert2  │
│   Hover-to-Expand Sidebar • Split-Screen Dual-Section Auth Portal      │
│   Live Low-Stock Alert Bell • Dynamic In-Memory QR Code Tagging        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP / REST / JSON
┌───────────────────────────────────▼────────────────────────────────────┐
│                    ROUTING & MIDDLEWARE LAYER                          │
│   Session Authentication • CSRF Verification • RBAC Authorization      │
│   CORS Headers • Global Context Processors (`erp_core`)                │
│   Automated Action Interceptor & Audit Trail Dispatcher                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                     BUSINESS DOMAIN LOGIC (15 APPS)                    │
│                                                                        │
│   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌────────────┐ │
│   │   Dashboard   │ │     Sales     │ │   Purchases   │ │  Products  │ │
│   └───────────────┘ └───────────────┘ └───────────────┘ └────────────┘ │
│   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌────────────┐ │
│   │   Inventory   │ │ Manufacturing │ │ Distribution  │ │  Invoices  │ │
│   └───────────────┘ └───────────────┘ └───────────────┘ └────────────┘ │
│   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌────────────┐ │
│   │   Payments    │ │    Ledger     │ │    Reports    │ │ Roles/User │ │
│   └───────────────┘ └───────────────┘ └───────────────┘ └────────────┘ │
│   ┌───────────────┐ ┌───────────────┐                                  │
│   │   Audit Log   │ │ Bulk Importer │                                  │
│   └───────────────┘ └───────────────┘                                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    DATA PERSISTENCE & ORM LAYER                        │
│   Django ORM • ACID Transactions • Aggregations & Query Optimization  │
│   PostgreSQL (Production) / SQLite (Development) • Redis Cache Ready   │
└────────────────────────────────────────────────────────────────────────┘
2. Domain Data Flow Diagramgraph TD
    User([Enterprise User / Admin]) -->|Auth / Dual Login| Auth[Authentication Module]
    Auth --> Dash[Executive Dashboard]

    subgraph Procurement Pipeline
        Vendor[Suppliers] --> Purchases[Purchase Orders]
        Purchases --> InvIn[Goods Receipt / Stock In]
    end

    subgraph Manufacturing & Assembly
        InvIn --> BOM[Bills of Materials - BOM]
        BOM --> WorkOrders[Work Orders & Assembly]
        WorkOrders --> FinishedGoods[Finished Stock SKUs]
    end

    subgraph Sales & Fulfillment
        FinishedGoods --> Sales[Sales Orders]
        Sales --> Distribution[Logistics & Dispatch]
        Distribution --> Invoices[Invoice Generator]
    end

    subgraph Financial Accounting & Governance
        Invoices --> Ledger[Double-Entry General Ledger]
        Payments[Collections & Vouchers] --> Ledger
        Purchases --> Payables[Accounts Payable]
        Payables --> Ledger
        Ledger --> Reports[Financial Statements / P&L]
        AllModules[ERP Actions] -.->|Signal Trigger| AuditTrail[Enterprise Audit Trail]
    end

    Dash -->|Live KPIs| Reports
📦 Core Domain Modules Breakdown#ModuleApp DirectoryCore Capabilities & Business Responsibilities1Executive Dashboarddashboard/Real-time KPI summary (Sales, Receivables, Payables, Stock Valuation), Chart.js visual analytics (Sales Trends, Category Breakdown), CDN resilient loaders, Aging accounts overview.2Product & Catalogproducts/Multi-category hierarchical SKU catalogue, Dynamic In-Memory QR Code Generator (qrcode + Pillow), printable warehouse tag labels, supplier mapping, cost/sale price tiers, batch tracking.3Bulk Data Importerproducts/High-throughput CSV & Excel (openpyxl) product importer with atomic transaction rollback, validation safeguards, error counters, and downloadable template support.4Sales Order Managementsales/Order capture, quotation-to-order pipeline, dynamic client credit limit validation, line-item tax calculations, order statuses (Draft, Confirmed, Dispatched, Invoiced).5Purchases & Procurementpurchases/Vendor management, RFQ, Purchase Orders (PO), landed cost allocations, receiving notes, automated payable voucher triggers.6Inventory & Warehousesinventory/Multi-warehouse stock tracking, bin locations, stock movements (Transfer, Adjustment, Damage write-off), Live Navbar Low-Stock Alert Bell Engine, reorder level alerts.7Manufacturing & Assemblymanufacturing/Multi-level Bill of Materials (BOM), production staging, raw material reservations, labor/overhead costing, scrap tracking, assembly work orders.8Logistics & Distributiondistribution/Consignment assignment, dispatch manifests, carrier tracking numbers, delivery confirmations, vehicle fleet allocation.9Invoicing & Format Engineinvoices/Automated invoice generation from dispatches, custom Drag-and-Drop Invoice Format Builder, customizable tax heads, multi-currency layout.10Payments & Reconciliationspayments/Customer collection receipts, vendor disbursements, partial payment allocations, bank/cash reconciliation vouchers.11General & Client Ledgerledger/Automated double-entry journals, chart of accounts, party-wise debit/credit ledgers, receivables aging buckets (0-30, 31-60, 61-90, 90+ days).12Reports & Intelligencereports_app/Sales breakdown, inventory valuation, Profit & Loss (P&L), Trial Balance, Balance Sheet, automated PDF export (ReportLab) & Excel generation (openpyxl).13Enterprise Audit Trailaudit_log/System-wide activity logger (ActivityLog), capturing actor, timestamp, action type (CREATE/UPDATE/EXPORT), module origin, and client IP address for regulatory compliance.14Roles & Permissions (RBAC)roles/Fine-grained permission matrix across all modules, role assignments (Admin, Finance Manager, Inventory Clerk, Sales Rep, Auditor).15User Administrationusers_app/User account provisioning, multi-branch assignment, status toggling, last activity tracking, security compliance.16Authentication Portaltemplates/auth/Two-column split-screen layout with enterprise branding showcase, interactive 1-click demo fill (admin / admin123), password reveal, session persistence.🎨 UI/UX Design System & Aesthetic StandardThe system follows an enterprise design language emphasizing clarity, density, and responsive micro-interactions:Primary Palette: Enterprise Royal Blue (#1E5EFF), Midnight Dark Navy (#0B132B / #0D1F55), Pure Surface (#FFFFFF), Soft Borders (#E2E8F0).Hover-to-Expand Collapsible Sidebar:Default collapsed mini-state (72px) maximizes data density for grids and tables.Hardware-accelerated hover expansion (260px in 250ms) floats over content with elevated shadow (box-shadow: 10px 0 36px rgba(5, 15, 45, 0.42)).Persistent pin/unpin state stored in browser localStorage.Zero CSS-Tailwind Conflict: Tailwind utilities strictly use the tw- prefix (e.g. tw-sticky, tw-flex, tw-gap-4), preventing conflicts with Bootstrap 5.3 components.Component Kit:Real-Time Low-Stock Navbar Notification DropdownToast system (ERP.toast())SweetAlert2 confirmation dialogs (ERP.confirmDelete())Select2 searchable select dropdowns with Bootstrap 5 skinFlatpickr date range pickersChart.js canvas renderers with graceful offline CDN fallback⚙️ Technology StackFrontend:
├── Django Template Language (DTL) 6.x / 5.x
├── Bootstrap 5.3.3 (Modals, Offcanvas, Dropdowns, Grid)
├── Tailwind CSS (Prefixed: tw-*)
├── Vanilla JavaScript (ES6+ Modules, zero heavy framework bloat)
├── Chart.js 4.x (Financial Analytics & Trend Lines)
├── Bootstrap Icons 1.11.3 & FontAwesome
├── Select2 4.1 & Flatpickr
└── SweetAlert2 11.x

Backend & Core:
├── Python 3.14+ / 3.10+
├── Django 6.0.8 / 5.2 (High-throughput WSGI/ASGI)
├── Django REST Framework 3.17.1 (JSON endpoints)
├── ReportLab (Vector PDF Generation Engine)
├── openpyxl (High-performance Excel Spreadsheet Builder)
├── qrcode & Pillow (In-memory QR/Barcode Generation)
├── django-cors-headers
└── SQLite3 (Dev) / PostgreSQL + Redis (Production Ready)
🚀 Quick Start & Installation Guide1. PrerequisitesPython 3.10+ (Recommended: Python 3.12 or 3.14)Git installedModern Web Browser (Chrome, Firefox, Safari, Edge)2. Clone and Setup Environment# Clone the repository
git clone https://github.com/AHMAD1237656/textile-erp-suite.git
cd textile-erp-suite

# Create virtual environment (Windows Powershell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# (Linux / macOS)
# python3 -m venv venv
# source venv/bin/activate
3. Install Dependenciespip install -r requirements.txt
4. Database Setup & Migrations# Run schema migrations across all apps
python manage.py makemigrations
python manage.py migrate
5. Seed Initial Base Data & Superuser# Create or verify admin credentials
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@techimport.com', 'admin123')
    print('Superuser created: admin / admin123')
else:
    print('Superuser admin already exists')
"
6. Run Development Serverpython manage.py runserver 127.0.0.1:8000
Open your browser at: http://127.0.0.1:8000/🔑 Default Credentials (Out-of-the-Box)The login screen features an automated One-Click Demo Fill button for instant administrative access:URL: http://127.0.0.1:8000/login/Username: adminPassword: admin123Role: System Administrator (Full Unrestricted Access)📁 Project Directory Treetextile-erp-suite/
├── manage.py
├── db.sqlite3
├── README.md
├── requirements.txt
├── erp_core/                 # Master configuration, settings & context processors
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── context_processors.py # Global permissions, notifications, ERP metadata
│
├── audit_log/                # Enterprise Activity Log & Compliance Tracker
│   ├── models.py             # ActivityLog model definition
│   ├── views.py              # Log listing and filtering views
│   └── urls.py
│
├── dashboard/                # Executive dashboard & real-time analytics
│   ├── urls.py
│   ├── views.py
│   └── models.py
│
├── products/                 # Catalog, SKUs, Categories, QR generator, CSV/Excel bulk import
│   ├── qr_utils.py           # In-memory Pillow/qrcode generator
│   ├── views.py              # Product CRUD & Bulk import handlers
│   └── urls.py
│
├── sales/                    # Sales orders, quotes, dispatching
├── purchases/                # POs, Supplier directory, receiving
├── inventory/                # Multi-warehouse stock, ledger movements, low-stock alerts
├── manufacturing/            # BOM formulas, work orders, scrap
├── distribution/             # Consignment dispatches & tracking
├── invoices/                 # Tax invoices & custom format builder
├── payments/                 # Receipts, vouchers, reconciliations
├── ledger/                   # Double-entry general & client ledgers
├── reports_app/              # P&L, balance sheets, ReportLab PDF / openpyxl Excel exports
├── roles/                    # RBAC permissions matrix
├── users_app/                # Employee user accounts
│
├── static/                   # Compiled & static enterprise assets
│   ├── css/
│   │   └── main.css          # Design system variables, layout, animations
│   └── js/
│       ├── main.js
│       └── modules/
│           ├── dashboard.js  # Chart.js renderers & CDN resilient loaders
│           └── low_stock_alerts.js # Live pollers for inventory warnings
│
└── templates/                # Server-rendered DTL templates
    ├── base.html             # Global shell layout
    ├── auth/
    │   └── login.html        # 2-section split-screen login page
    ├── audit_log/            # Governance trail table UI
    ├── partials/
    │   ├── navbar.html       # Topbar with low-stock notification badge
    │   ├── sidebar.html      # Hover-to-expand multi-app sidebar
    │   └── quick_action_modal.html
    ├── dashboard/
    ├── products/             # Detail view with QR label & Bulk Import modals
    ├── sales/
    ├── purchases/
    ├── inventory/
    ├── manufacturing/
    ├── distribution/
    ├── invoices/
    ├── payments/
    ├── ledger/
    ├── reports_app/
    ├── roles/
    └── users_app/
⌨️ Global Keyboard ShortcutsShortcutAction DescriptionTarget Element/Instant global navigation searchFocuses .navbar-search-inputN or nQuick Action / New Document modalTriggers #btn-newEscDismiss active modal or overlayCloses .modal.show🛡️ Security & Enterprise Best PracticesCSRF Protection: All form submissions and asynchronous fetch() API calls pass valid Django CSRF tokens via window.ERP.csrfToken.Audit Logging: Sensitive actions (file exports, bulk modifications, administrative changes) are tracked in real-time with actor details and IP tracking.RBAC Enforcement: Server-side permission guards at both view layer and template presentation layer ({% if erp_permissions.can_manage_* %}).SQL Injection Prevention: 100% ORM parameterized querying; raw unescaped queries are strictly prohibited.XSS Sanitization: Template auto-escaping active across all dynamic content outputs.Session Security: 24-hour rolling session cookie timeout with security headers (X-Frame-Options: DENY, X-Content-Type-Options: nosniff).👨‍💻 Engineering Credits & AuthorsOriginal Architecture & Lead Design: Muhammad DanishFull-Stack Implementation & Platform Enhancements: Muhammad AhmadContributions: Dynamic QR Code Tracking, Real-Time Low-Stock Notification System, Automated Audit Trail Module, Multi-Format Bulk Importers, ReportLab/openpyxl Document Exporters, and Resilient Dashboard Chart Architecture.📄 License & Intellectual PropertyCopyright © 2026 TechImport Enterprise ERP Suite.Provided for portfolio, commercial demonstration, and enterprise deployment evaluation.