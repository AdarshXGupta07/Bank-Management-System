const API = "http://localhost:5000";
const page = document.body.dataset.page;
let currentPage = 1;
const pageSize = 5;

const showAlert = (message, type = "success") => {
  const el = document.getElementById("alert");
  if (!el) return;
  el.className = `alert ${type}`;
  el.style.display = "block";
  el.textContent = message;
  setTimeout(() => (el.style.display = "none"), 3000);
};

const submitJSON = async (url, method, data) => {
  const res = await fetch(`${API}${url}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  const payload = await res.json();
  if (!res.ok) throw new Error(payload.message || "Request failed");
  return payload;
};

const renderTable = (id, rows) => {
  const table = document.getElementById(id);
  if (!table) return;
  if (!rows.length) {
    table.innerHTML = "<tr><td>No records found.</td></tr>";
    return;
  }
  const headers = Object.keys(rows[0]);
  table.innerHTML = `<tr>${headers.map((h) => `<th>${h}</th>`).join("")}</tr>` +
    rows.map((r) => `<tr>${headers.map((h) => `<td>${r[h] ?? ""}</td>`).join("")}</tr>`).join("");
};

const formDataObj = (form) => Object.fromEntries(new FormData(form).entries());

async function loadDashboard() {
  const stats = await (await fetch(`${API}/dashboard/stats`)).json();
  Object.entries(stats).forEach(([k, v]) => {
    const el = document.getElementById(k);
    if (el) el.textContent = v;
  });
  renderTable("branchTable", await (await fetch(`${API}/branches`)).json());
  renderTable("employeeTable", await (await fetch(`${API}/employees`)).json());
}

async function loadCustomers() {
  const data = await (await fetch(`${API}/customers`)).json();
  const q = (document.getElementById("searchInput")?.value || "").toLowerCase();
  const filtered = data.filter((r) => Object.values(r).join(" ").toLowerCase().includes(q));
  const paginated = filtered.slice((currentPage - 1) * pageSize, currentPage * pageSize);
  renderTable("customerTable", paginated);
}

async function loadAccounts() { renderTable("accountTable", await (await fetch(`${API}/accounts`)).json()); }
async function loadLoans() { renderTable("loanTable", await (await fetch(`${API}/loans`)).json()); }
async function loadPayments() { renderTable("paymentTable", await (await fetch(`${API}/payments`)).json()); }

const bind = (id, cb) => document.getElementById(id)?.addEventListener("submit", cb);

bind("branchForm", async (e) => { e.preventDefault(); try { await submitJSON("/branch/add", "POST", formDataObj(e.target)); showAlert("Branch added"); e.target.reset(); loadDashboard(); } catch (err) { showAlert(err.message, "error"); } });
bind("employeeForm", async (e) => { e.preventDefault(); try { await submitJSON("/employee/add", "POST", formDataObj(e.target)); showAlert("Employee added"); e.target.reset(); loadDashboard(); } catch (err) { showAlert(err.message, "error"); } });
bind("assignForm", async (e) => { e.preventDefault(); try { await submitJSON("/employee/assign", "POST", formDataObj(e.target)); showAlert("Employee assigned"); e.target.reset(); } catch (err) { showAlert(err.message, "error"); } });

bind("customerForm", async (e) => { e.preventDefault(); try { await submitJSON("/customer/add", "POST", formDataObj(e.target)); showAlert("Customer added"); e.target.reset(); loadCustomers(); } catch (err) { showAlert(err.message, "error"); } });
bind("accountForm", async (e) => { e.preventDefault(); try { await submitJSON("/account/create", "POST", formDataObj(e.target)); showAlert("Account created"); e.target.reset(); loadAccounts(); } catch (err) { showAlert(err.message, "error"); } });
bind("depositForm", async (e) => { e.preventDefault(); try { await submitJSON("/account/deposit", "POST", formDataObj(e.target)); showAlert("Deposit successful"); e.target.reset(); loadAccounts(); } catch (err) { showAlert(err.message, "error"); } });
bind("withdrawForm", async (e) => { e.preventDefault(); try { await submitJSON("/account/withdraw", "POST", formDataObj(e.target)); showAlert("Withdrawal successful"); e.target.reset(); loadAccounts(); } catch (err) { showAlert(err.message, "error"); } });
bind("loanForm", async (e) => { e.preventDefault(); try { await submitJSON("/loan/apply", "POST", formDataObj(e.target)); showAlert("Loan applied"); e.target.reset(); loadLoans(); } catch (err) { showAlert(err.message, "error"); } });
bind("approveLoanForm", async (e) => { e.preventDefault(); try { await submitJSON("/loan/approve", "POST", formDataObj(e.target)); showAlert("Loan approved"); e.target.reset(); loadLoans(); } catch (err) { showAlert(err.message, "error"); } });
bind("paymentForm", async (e) => { e.preventDefault(); try { await submitJSON("/payment/add", "POST", formDataObj(e.target)); showAlert("Payment recorded"); e.target.reset(); loadPayments(); } catch (err) { showAlert(err.message, "error"); } });

document.getElementById("searchInput")?.addEventListener("input", () => { currentPage = 1; loadCustomers(); });
document.getElementById("prevPage")?.addEventListener("click", () => { if (currentPage > 1) currentPage--; loadCustomers(); });
document.getElementById("nextPage")?.addEventListener("click", () => { currentPage++; loadCustomers(); });

(async () => {
  try {
    if (page === "dashboard") await loadDashboard();
    if (page === "customers") await loadCustomers();
    if (page === "accounts") await loadAccounts();
    if (page === "loans") await loadLoans();
    if (page === "payments") await loadPayments();
  } catch {
    showAlert("Unable to reach backend API. Start Flask server on port 5000.", "error");
  }
})();
