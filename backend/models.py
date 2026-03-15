from datetime import date

from sqlalchemy import CheckConstraint, UniqueConstraint

from database import db


class Bank(db.Model):
    __tablename__ = "bank"

    code = db.Column(db.String(20), primary_key=True)
    b_name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(255), nullable=False)

    branches = db.relationship("Branch", backref="bank", cascade="all, delete-orphan", lazy=True)


class Branch(db.Model):
    __tablename__ = "branch"

    branch_code = db.Column(db.String(20), primary_key=True)
    branch_name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    bank_code = db.Column(db.String(20), db.ForeignKey("bank.code"), nullable=False)


class Customer(db.Model):
    __tablename__ = "customer"
    __table_args__ = (UniqueConstraint("mobile_no", name="unique_mobile"),)

    cust_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    mobile_no = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    bank_code = db.Column(db.String(20), db.ForeignKey("bank.code"), nullable=True)
    managed_by = db.Column(db.String(20), db.ForeignKey("employee.emp_id"), nullable=True)

    accounts = db.relationship("Account", backref="customer", cascade="all, delete-orphan", lazy=True)
    loans = db.relationship("Loan", backref="customer", cascade="all, delete-orphan", lazy=True)


class Account(db.Model):
    __tablename__ = "account"
    __table_args__ = (
        CheckConstraint("balance >= 0", name="chk_balance"),
        CheckConstraint("account_type in ('SAVING', 'CURRENT')", name="chk_account_type"),
    )

    account_no = db.Column(db.String(20), primary_key=True)
    balance = db.Column(db.Float, nullable=False, default=0)
    account_type = db.Column(db.String(20), nullable=False)
    cust_id = db.Column(db.String(20), db.ForeignKey("customer.cust_id"), nullable=False)

    saving = db.relationship("Saving", backref="account", uselist=False, cascade="all, delete-orphan")
    current = db.relationship("Current", backref="account", uselist=False, cascade="all, delete-orphan")


class Saving(db.Model):
    __tablename__ = "saving"

    account_no = db.Column(db.String(20), db.ForeignKey("account.account_no"), primary_key=True)
    interest_rate = db.Column(db.Float, nullable=False, default=4.0)


class Current(db.Model):
    __tablename__ = "current"

    account_no = db.Column(db.String(20), db.ForeignKey("account.account_no"), primary_key=True)
    overdraft_limit = db.Column(db.Float, nullable=False, default=0)


class Employee(db.Model):
    __tablename__ = "employee"
    __table_args__ = (UniqueConstraint("mobile_no", name="unique_employee_mobile"),)

    emp_id = db.Column(db.String(20), primary_key=True)
    emp_name = db.Column(db.String(120), nullable=False)
    mobile_no = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(255), nullable=False)

    customers = db.relationship("Customer", backref="manager", lazy=True)


class Loan(db.Model):
    __tablename__ = "loan"
    __table_args__ = (CheckConstraint("amount > 0", name="chk_loan"),)

    loan_no = db.Column(db.String(20), primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    cust_id = db.Column(db.String(20), db.ForeignKey("customer.cust_id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="PENDING")

    payments = db.relationship("Payment", backref="loan", cascade="all, delete-orphan", lazy=True)


class Payment(db.Model):
    __tablename__ = "payment"
    __table_args__ = (CheckConstraint("payment_amount > 0", name="chk_payment_amount"),)

    payment_no = db.Column(db.String(20), primary_key=True)
    payment_date = db.Column(db.Date, nullable=False, default=date.today)
    payment_amount = db.Column(db.Float, nullable=False)
    loan_no = db.Column(db.String(20), db.ForeignKey("loan.loan_no"), nullable=False)
