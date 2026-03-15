# Bank Management System (Full Stack)

A complete **Bank Management System Website** with modern responsive frontend and Flask REST API backend.

## Project Description

This project implements a normalized banking domain with the entities from the ER model:
- BANK
- BRANCH
- CUSTOMER
- ACCOUNT (ISA: SAVING / CURRENT)
- EMPLOYEE
- LOAN
- PAYMENT

It provides modules for dashboard analytics, customer/account/branch/employee management, loan workflow, and loan payments.

## Technology Stack

- **Frontend:** HTML5, CSS3, JavaScript (responsive dashboard UI)
- **Backend:** Python, Flask, Flask-RESTful, Flask-SQLAlchemy
- **Database:** PostgreSQL/MySQL compatible schema (and SQLite fallback for quick local run)

## Folder Structure

```text
bank-management-system/
│
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   ├── customers.html
│   ├── accounts.html
│   ├── loans.html
│   ├── payments.html
│   ├── css/
│   │     └── styles.css
│   └── js/
│         └── app.js
│
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   ├── database.py
│   └── requirements.txt
│
├── database/
│   └── schema.sql
│
├── documentation/
│   └── queries.md
│
└── README.md
```

## Installation Steps

1. Clone/open the project.
2. Create and activate virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

### Option A: PostgreSQL / MySQL
1. Create a database (e.g. `bank_db`).
2. Run `database/schema.sql` in your DB client.
3. Set `DATABASE_URL`:
   - PostgreSQL: `postgresql+psycopg2://user:pass@localhost:5432/bank_db`
   - MySQL: `mysql+pymysql://user:pass@localhost:3306/bank_db`

### Option B: Quick Local (SQLite)
If `DATABASE_URL` is not set, the app uses `sqlite:///bank_management.db` automatically.

## How to Run the Application

### Start backend
```bash
cd backend
python app.py
```
Backend URL: `http://localhost:5000`

### Start frontend
Use any static server:
```bash
cd frontend
python -m http.server 8080
```
Frontend URL: `http://localhost:8080`

## REST APIs

### Customer APIs
- `POST /customer/add`
- `GET /customers`
- `PUT /customer/update`
- `DELETE /customer/delete`

### Account APIs
- `POST /account/create`
- `GET /accounts`
- `POST /account/deposit`
- `POST /account/withdraw`

### Loan APIs
- `POST /loan/apply`
- `GET /loans`

### Payment APIs
- `POST /payment/add`
- `GET /payments`

Additional APIs included for dashboard, branch, employee, assignment, and loan approval.

## Complex Queries Section

All queries are present in `database/schema.sql`.

### Constraints (3)
1. Check non-negative account balance
2. Unique customer mobile number
3. Positive loan amount

### Aggregate Functions (3)
1. SUM of loan amount
2. AVG account balance
3. COUNT of customers

### Set Operations (3)
1. Accounts but no loans
2. Loans but no accounts
3. Both accounts and loans

### Subqueries (3)
1. Customers above average balance
2. Customer with highest loan
3. Accounts of customers with approved loans

### Joins (3)
1. Customer + account balance
2. Customer + loan details
3. Branch + bank names

### Views (3)
1. `customer_accounts`
2. `customer_loans`
3. `loan_payments`

### Triggers (3)
1. Prevent negative balance update
2. Set high-loan review logic
3. Payment audit logging

### Cursors (3)
1. Loan processing cursor
2. Overdue loan cursor
3. Account summation cursor

## Constraints & Normalization Notes

- PK/FK relationships are enforced across entities.
- CHECK constraints validate balances, loan amounts, statuses, and account types.
- Unique constraints on mobile numbers.
- ISA modeled through `saving` and `current` subtype tables with one-to-one relation to `account`.
- Design follows clean modular separation of frontend, backend, and database scripts.

## Features Included

- Responsive layout and sidebar navigation
- Dashboard metric cards
- Data entry forms
- Table views
- Search (customers)
- Pagination (customers)
- Success/error alerts
- Clean code structure with comments/docstrings
