-- Bank Management System SQL Schema (PostgreSQL-compatible core)

CREATE TABLE bank (
    code VARCHAR(20) PRIMARY KEY,
    b_name VARCHAR(120) NOT NULL,
    city VARCHAR(80) NOT NULL,
    address VARCHAR(255) NOT NULL
);

CREATE TABLE branch (
    branch_code VARCHAR(20) PRIMARY KEY,
    branch_name VARCHAR(120) NOT NULL,
    address VARCHAR(255) NOT NULL,
    bank_code VARCHAR(20) NOT NULL,
    CONSTRAINT fk_branch_bank FOREIGN KEY (bank_code) REFERENCES bank(code) ON DELETE CASCADE
);

CREATE TABLE employee (
    emp_id VARCHAR(20) PRIMARY KEY,
    emp_name VARCHAR(120) NOT NULL,
    mobile_no VARCHAR(15) NOT NULL UNIQUE,
    address VARCHAR(255) NOT NULL
);

CREATE TABLE customer (
    cust_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    mobile_no VARCHAR(15) NOT NULL UNIQUE,
    address VARCHAR(255) NOT NULL,
    bank_code VARCHAR(20),
    managed_by VARCHAR(20),
    CONSTRAINT fk_customer_bank FOREIGN KEY (bank_code) REFERENCES bank(code),
    CONSTRAINT fk_customer_employee FOREIGN KEY (managed_by) REFERENCES employee(emp_id)
);

CREATE TABLE account (
    account_no VARCHAR(20) PRIMARY KEY,
    balance NUMERIC(12,2) NOT NULL CHECK (balance >= 0),
    account_type VARCHAR(20) NOT NULL CHECK (account_type IN ('SAVING', 'CURRENT')),
    cust_id VARCHAR(20) NOT NULL,
    CONSTRAINT fk_account_customer FOREIGN KEY (cust_id) REFERENCES customer(cust_id) ON DELETE CASCADE
);

CREATE TABLE saving (
    account_no VARCHAR(20) PRIMARY KEY,
    interest_rate NUMERIC(5,2) NOT NULL DEFAULT 4.00 CHECK (interest_rate >= 0),
    CONSTRAINT fk_saving_account FOREIGN KEY (account_no) REFERENCES account(account_no) ON DELETE CASCADE
);

CREATE TABLE current_account (
    account_no VARCHAR(20) PRIMARY KEY,
    overdraft_limit NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (overdraft_limit >= 0),
    CONSTRAINT fk_current_account FOREIGN KEY (account_no) REFERENCES account(account_no) ON DELETE CASCADE
);

CREATE TABLE loan (
    loan_no VARCHAR(20) PRIMARY KEY,
    amount NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    cust_id VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
    CONSTRAINT fk_loan_customer FOREIGN KEY (cust_id) REFERENCES customer(cust_id) ON DELETE CASCADE
);

CREATE TABLE payment (
    payment_no VARCHAR(20) PRIMARY KEY,
    payment_date DATE NOT NULL,
    payment_amount NUMERIC(12,2) NOT NULL CHECK (payment_amount > 0),
    loan_no VARCHAR(20) NOT NULL,
    CONSTRAINT fk_payment_loan FOREIGN KEY (loan_no) REFERENCES loan(loan_no) ON DELETE CASCADE
);

-- ========================================================
-- 3.1 ADDING CONSTRAINTS (3+ queries)
-- ========================================================
-- Q1: Ensure account balance cannot be negative
ALTER TABLE account ADD CONSTRAINT chk_balance CHECK (balance >= 0);
-- Output: Account table now prevents negative balance.

-- Q2: Ensure unique mobile numbers for customers
ALTER TABLE customer ADD CONSTRAINT unique_mobile UNIQUE (mobile_no);
-- Output: Duplicate mobile numbers not allowed.

-- Q3: Ensure loan amount is positive
ALTER TABLE loan ADD CONSTRAINT chk_loan CHECK (amount > 0);
-- Output: Loan amounts must be greater than zero.

-- ========================================================
-- 3.2 AGGREGATE FUNCTIONS (3+ queries)
-- ========================================================
-- Q1: Find total loan amount issued
SELECT SUM(amount) AS total_loan_amount FROM loan;

-- Q2: Find average account balance
SELECT AVG(balance) AS avg_account_balance FROM account;

-- Q3: Count customers
SELECT COUNT(*) AS total_customers FROM customer;

-- ========================================================
-- 3.3 SET OPERATIONS (3+ queries)
-- ========================================================
-- Q1: Customers with accounts but no loans
SELECT cust_id FROM account
EXCEPT
SELECT cust_id FROM loan;

-- Q2: Customers with loans but no accounts
SELECT cust_id FROM loan
EXCEPT
SELECT cust_id FROM account;

-- Q3: Customers with both accounts and loans
SELECT cust_id FROM account
INTERSECT
SELECT cust_id FROM loan;

-- ========================================================
-- 3.4 SUBQUERIES (3+ queries)
-- ========================================================
-- Q1: Customers with balance greater than average balance
SELECT name
FROM customer
WHERE cust_id IN (
    SELECT cust_id FROM account
    WHERE balance > (SELECT AVG(balance) FROM account)
);

-- Q2: Customer with highest loan amount
SELECT name
FROM customer
WHERE cust_id = (
    SELECT cust_id FROM loan
    ORDER BY amount DESC LIMIT 1
);

-- Q3: Accounts belonging to customers who have approved loans
SELECT account_no, balance
FROM account
WHERE cust_id IN (
    SELECT cust_id FROM loan WHERE status = 'APPROVED'
);

-- ========================================================
-- 3.5 JOINS (3+ queries)
-- ========================================================
-- Q1: List customers with account balances
SELECT c.name, a.account_no, a.balance
FROM customer c
JOIN account a ON c.cust_id = a.cust_id;

-- Q2: List customers with loan details
SELECT c.name, l.loan_no, l.amount, l.status
FROM customer c
JOIN loan l ON c.cust_id = l.cust_id;

-- Q3: List branch and bank names
SELECT b.branch_name, bk.b_name
FROM branch b
JOIN bank bk ON b.bank_code = bk.code;

-- ========================================================
-- 3.6 VIEWS (3+ queries)
-- ========================================================
CREATE VIEW customer_accounts AS
SELECT c.name, a.account_no, a.balance
FROM customer c
JOIN account a ON c.cust_id = a.cust_id;

CREATE VIEW customer_loans AS
SELECT c.name, l.loan_no, l.amount, l.status
FROM customer c
JOIN loan l ON c.cust_id = l.cust_id;

CREATE VIEW loan_payments AS
SELECT l.loan_no, p.payment_no, p.payment_date, p.payment_amount
FROM loan l
JOIN payment p ON l.loan_no = p.loan_no;

-- ========================================================
-- 3.7 TRIGGERS (MySQL syntax, 3 examples)
-- ========================================================
-- Q1: Prevent negative balance on update
-- DELIMITER $$
-- CREATE TRIGGER check_balance_before_update
-- BEFORE UPDATE ON account
-- FOR EACH ROW
-- BEGIN
--   IF NEW.balance < 0 THEN
--     SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient balance';
--   END IF;
-- END $$
-- DELIMITER ;

-- Q2: Auto-set loan status when amount exceeds threshold
-- DELIMITER $$
-- CREATE TRIGGER set_high_loan_review
-- BEFORE INSERT ON loan
-- FOR EACH ROW
-- BEGIN
--   IF NEW.amount > 1000000 THEN
--     SET NEW.status = 'PENDING';
--   END IF;
-- END $$
-- DELIMITER ;

-- Q3: Log payment inserts (requires payment_audit table)
-- DELIMITER $$
-- CREATE TRIGGER payment_audit_trigger
-- AFTER INSERT ON payment
-- FOR EACH ROW
-- BEGIN
--   INSERT INTO payment_audit(payment_no, action_time)
--   VALUES (NEW.payment_no, NOW());
-- END $$
-- DELIMITER ;

-- ========================================================
-- 3.8 CURSORS (MySQL procedure syntax, 3 examples)
-- ========================================================
-- Q1: Cursor for loan processing
-- DECLARE loan_cursor CURSOR FOR SELECT loan_no, amount FROM loan;

-- Q2: Cursor to iterate overdue loans
-- DECLARE overdue_cursor CURSOR FOR
-- SELECT loan_no FROM loan WHERE status = 'PENDING';

-- Q3: Cursor to sum customer balances manually
-- DECLARE account_cursor CURSOR FOR
-- SELECT balance FROM account WHERE cust_id = in_cust_id;
