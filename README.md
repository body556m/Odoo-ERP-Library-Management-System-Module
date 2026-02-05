# Odoo-ERP-Library-Management-System-Module
A full-featured Library Management System built with Odoo, designed to manage books, members, borrowing workflows, and reporting with an ERP-oriented architecture.

## 📘 About
This project is a custom Odoo module that implements a complete Library Management System within the Odoo framework. It provides tools for managing books, members, borrow/return flows, fines, and reports — all following Odoo’s modular architecture, security rules, and ORM paradigms.

## 🚀 Features

### 📚 Book Management
- Add, edit, and delete book records (title, ISBN, author, publisher, edition)
- Book inventory tracking
- Category and language classification

### 👤 Member Management
- Add and manage members
- Membership types and expiry tracking
- Generate library cards

### 📘 Borrowing & Returning
- Issue and return books with due date calculation
- Limit books per membership type
- Automatically update book stock

### ⏱️ Workflow Rules
- Automated fine calculation for late returns
- Notifications or reminders for due dates
- Block members with overdue books

### 📊 Reports & Insights
- Reports for issued books, members activity, and book inventory
- PDF / XLSX export (configurable)

### 🛡️ Security & Access
- Role-based access controls for librarians, managers, and users


## 🧱 Module Structure

- `controllers/` — HTTP controllers (if web UI endpoints)
- `data/` — Data files (demo or initial configuration)
- `demo/` — Demo records for testing or demo mode
- `lib_models/` — Python models defining business logic
- `reports/` — Report templates and definitions
- `security/` — Access control rules and security groups
- `static/` — Static assets (CSS, JS, images)
- `tests/` — Automated tests
- `views/` — XML views for forms, trees, kanbans
- `wizard/` — Wizard dialogs for multi-step interactions
- `__manifest__.py` — Module metadata (name, dependencies, version)



