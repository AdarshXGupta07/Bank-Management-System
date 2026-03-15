from datetime import datetime

from flask import request
from flask_restful import Api, Resource

from database import db
from models import Account, Bank, Branch, Current, Customer, Employee, Loan, Payment, Saving


api = Api()


def _json(model):
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}


class DashboardStatsAPI(Resource):
    def get(self):
        return {
            "total_customers": Customer.query.count(),
            "total_accounts": Account.query.count(),
            "total_loans": Loan.query.count(),
            "total_branches": Branch.query.count(),
        }


class CustomerAddAPI(Resource):
    def post(self):
        data = request.get_json(force=True)
        customer = Customer(**data)
        db.session.add(customer)
        db.session.commit()
        return {"message": "Customer added successfully", "customer": _json(customer)}, 201


class CustomerListAPI(Resource):
    def get(self):
        customers = Customer.query.order_by(Customer.name.asc()).all()
        return [_json(c) for c in customers]


class CustomerUpdateAPI(Resource):
    def put(self):
        data = request.get_json(force=True)
        cust_id = data.get("cust_id")
        customer = Customer.query.get_or_404(cust_id)
        for field in ["name", "mobile_no", "address", "bank_code", "managed_by"]:
            if field in data:
                setattr(customer, field, data[field])
        db.session.commit()
        return {"message": "Customer updated", "customer": _json(customer)}


class CustomerDeleteAPI(Resource):
    def delete(self):
        data = request.get_json(force=True)
        customer = Customer.query.get_or_404(data.get("cust_id"))
        db.session.delete(customer)
        db.session.commit()
        return {"message": "Customer deleted"}


class AccountCreateAPI(Resource):
    def post(self):
        data = request.get_json(force=True)
        account = Account(
            account_no=data["account_no"],
            balance=float(data.get("balance", 0)),
            account_type=data["account_type"].upper(),
            cust_id=data["cust_id"],
        )
        db.session.add(account)
        if account.account_type == "SAVING":
            db.session.add(Saving(account_no=account.account_no, interest_rate=float(data.get("interest_rate", 4.0))))
        else:
            db.session.add(Current(account_no=account.account_no, overdraft_limit=float(data.get("overdraft_limit", 0))))
        db.session.commit()
        return {"message": "Account created", "account": _json(account)}, 201


class AccountListAPI(Resource):
    def get(self):
        accounts = Account.query.order_by(Account.account_no.asc()).all()
        return [_json(a) for a in accounts]


class AccountDepositAPI(Resource):
    def post(self):
        data = request.get_json(force=True)
        account = Account.query.get_or_404(data.get("account_no"))
        amount = float(data.get("amount", 0))
        if amount <= 0:
            return {"message": "Deposit amount must be positive"}, 400
        account.balance += amount
        db.session.commit()
        return {"message": "Deposit successful", "balance": account.balance}


class AccountWithdrawAPI(Resource):
    def post(self):
        data = request.get_json(force=True)
        account = Account.query.get_or_404(data.get("account_no"))
        amount = float(data.get("amount", 0))
        if amount <= 0:
            return {"message": "Withdrawal amount must be positive"}, 400
        if account.balance - amount < 0:
            return {"message": "Insufficient balance"}, 400
        account.balance -= amount
        db.session.commit()
        return {"message": "Withdrawal successful", "balance": account.balance}


class BranchAddAPI(Resource):
    def post(self):
        data = request.get_json(force=True)
        branch = Branch(**data)
        db.session.add(branch)
        db.session.commit()
        return {"message": "Branch added", "branch": _json(branch)}, 201


class BranchListAPI(Resource):
    def get(self):
        branches = Branch.query.order_by(Branch.branch_name.asc()).all()
        return [_json(b) for b in branches]


class BranchDeleteAPI(Resource):
    def delete(self):
        data = request.get_json(force=True)
        branch = Branch.query.get_or_404(data.get("branch_code"))
        db.session.delete(branch)
        db.session.commit()
        return {"message": "Branch deleted"}


class EmployeeAddAPI(Resource):
    def post(self):
        data = request.get_json(force=True)
        employee = Employee(**data)
        db.session.add(employee)
        db.session.commit()
        return {"message": "Employee added", "employee": _json(employee)}, 201


class EmployeeListAPI(Resource):
    def get(self):
        employees = Employee.query.order_by(Employee.emp_name.asc()).all()
        return [_json(e) for e in employees]


class AssignEmployeeAPI(Resource):
    def post(self):
        data = request.get_json(force=True)
        customer = Customer.query.get_or_404(data.get("cust_id"))
        employee = Employee.query.get_or_404(data.get("emp_id"))
        customer.managed_by = employee.emp_id
        db.session.commit()
        return {"message": "Employee assigned", "customer": _json(customer)}


class LoanApplyAPI(Resource):
    def post(self):
        data = request.get_json(force=True)
        loan = Loan(loan_no=data["loan_no"], amount=float(data["amount"]), cust_id=data["cust_id"])
        db.session.add(loan)
        db.session.commit()
        return {"message": "Loan application submitted", "loan": _json(loan)}, 201


class LoanListAPI(Resource):
    def get(self):
        loans = Loan.query.order_by(Loan.loan_no.asc()).all()
        return [_json(l) for l in loans]


class LoanApproveAPI(Resource):
    def post(self):
        data = request.get_json(force=True)
        loan = Loan.query.get_or_404(data.get("loan_no"))
        loan.status = "APPROVED"
        db.session.commit()
        return {"message": "Loan approved", "loan": _json(loan)}


class PaymentAddAPI(Resource):
    def post(self):
        data = request.get_json(force=True)
        payment_date = data.get("payment_date")
        parsed_date = datetime.strptime(payment_date, "%Y-%m-%d").date() if payment_date else datetime.utcnow().date()
        payment = Payment(
            payment_no=data["payment_no"],
            payment_date=parsed_date,
            payment_amount=float(data["payment_amount"]),
            loan_no=data["loan_no"],
        )
        db.session.add(payment)
        db.session.commit()
        return {"message": "Payment recorded", "payment": _json(payment)}, 201


class PaymentListAPI(Resource):
    def get(self):
        payments = Payment.query.order_by(Payment.payment_date.desc()).all()
        return [_json(p) for p in payments]


class BankSeedAPI(Resource):
    def post(self):
        data = request.get_json(force=True)
        bank = Bank(**data)
        db.session.add(bank)
        db.session.commit()
        return {"message": "Bank added", "bank": _json(bank)}, 201


def init_routes(app):
    api.init_app(app)

    api.add_resource(DashboardStatsAPI, "/dashboard/stats")

    api.add_resource(CustomerAddAPI, "/customer/add")
    api.add_resource(CustomerListAPI, "/customers")
    api.add_resource(CustomerUpdateAPI, "/customer/update")
    api.add_resource(CustomerDeleteAPI, "/customer/delete")

    api.add_resource(AccountCreateAPI, "/account/create")
    api.add_resource(AccountListAPI, "/accounts")
    api.add_resource(AccountDepositAPI, "/account/deposit")
    api.add_resource(AccountWithdrawAPI, "/account/withdraw")

    api.add_resource(BranchAddAPI, "/branch/add")
    api.add_resource(BranchListAPI, "/branches")
    api.add_resource(BranchDeleteAPI, "/branch/delete")

    api.add_resource(EmployeeAddAPI, "/employee/add")
    api.add_resource(EmployeeListAPI, "/employees")
    api.add_resource(AssignEmployeeAPI, "/employee/assign")

    api.add_resource(LoanApplyAPI, "/loan/apply")
    api.add_resource(LoanListAPI, "/loans")
    api.add_resource(LoanApproveAPI, "/loan/approve")

    api.add_resource(PaymentAddAPI, "/payment/add")
    api.add_resource(PaymentListAPI, "/payments")

    api.add_resource(BankSeedAPI, "/bank/add")
