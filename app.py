"""Flask spending tracker with persistent JSON storage and reporting views."""

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Flask, flash, redirect, render_template, request, url_for


app = Flask(__name__)
app.secret_key = "team4-spending-tracker-secret"

APP_TITLE = "Team 4 Spending Tracker"
CATEGORIES = ["Rent", "Bills", "Food", "Gas", "Entertainment"]
DATA_FILE = Path("expenses.json")
DATE_FORMAT = "%Y-%m-%d"
MONTH_FORMAT = "%Y-%m"


def load_expenses():
    """Load expenses from disk, returning an empty list if missing or invalid."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    expenses = data if isinstance(data, list) else []
    if ensure_expense_ids(expenses):
        save_expenses(expenses)
    return expenses


def save_expenses(expenses):
    """Persist expenses list to disk as JSON."""
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=2)


def parse_date(date_text, fmt):
    """Parse a date string with the given format."""
    try:
        return datetime.strptime(date_text, fmt).date()
    except ValueError:
        return None


def parse_entry_date(entry):
    """Parse the expense date field from an entry."""
    return parse_date(entry.get("date", ""), DATE_FORMAT)


def ensure_expense_ids(expenses):
    """Ensure each expense has a stable ID for edit/delete actions."""
    updated = False
    for entry in expenses:
        if not entry.get("id"):
            entry["id"] = uuid4().hex
            updated = True
    return updated


def find_expense_index(expenses, expense_id):
    """Find expense index by ID and return -1 if not found."""
    for index, entry in enumerate(expenses):
        if entry.get("id") == expense_id:
            return index
    return -1


def redirect_to_index(month_filter):
    """Redirect to index while preserving month filter state if provided."""
    month_filter = (month_filter or "").strip()
    if month_filter:
        return redirect(url_for("index", month=month_filter))
    return redirect(url_for("index"))


def sorted_expenses_by_date(expenses):
    """Sort expenses by date; invalid dates appear last."""

    def sort_key(entry):
        entry_date = parse_entry_date(entry)
        return (entry_date is None, entry_date or datetime.max.date())

    return sorted(expenses, key=sort_key)


def normalize_amount(amount_text):
    """Convert amount text to rounded float or return None if invalid."""
    try:
        amount = round(float(amount_text), 2)
    except (TypeError, ValueError):
        return None

    if amount < 0:
        return None
    return amount


def filter_expenses_by_month(expenses, month_filter):
    """Filter expenses by YYYY-MM and return filtered list with display label."""
    if not month_filter:
        return expenses, "All Months", None

    month_date = parse_date(month_filter, MONTH_FORMAT)
    if month_date is None:
        return None, None, "Please use YYYY-MM for the month filter."

    filtered = []
    for entry in expenses:
        entry_date = parse_entry_date(entry)
        if entry_date and entry_date.year == month_date.year and entry_date.month == month_date.month:
            filtered.append(entry)

    return filtered, month_date.strftime("%B %Y"), None


def build_totals_by_category(expenses):
    """Build totals for each category and include unknown categories if present."""
    totals = {category: 0.0 for category in CATEGORIES}
    for entry in expenses:
        category = entry.get("category", "Unknown")
        amount = normalize_amount(entry.get("amount", 0.0)) or 0.0
        totals[category] = totals.get(category, 0.0) + amount
    return totals


def ordered_totals(totals):
    """Return totals list ordered by known categories, then extras alphabetically."""
    rows = []
    for category in CATEGORIES:
        rows.append({"category": category, "amount": totals.get(category, 0.0)})

    for category in sorted(c for c in totals.keys() if c not in CATEGORIES):
        rows.append({"category": category, "amount": totals[category]})

    return rows


def monthly_summary(expenses):
    """Build month grouped totals for dashboard summary cards."""
    grouped = {}
    for entry in expenses:
        entry_date = parse_entry_date(entry)
        if not entry_date:
            continue

        month_key = entry_date.strftime(MONTH_FORMAT)
        month_label = entry_date.strftime("%B %Y")

        if month_key not in grouped:
            grouped[month_key] = {
                "month_label": month_label,
                "totals": {category: 0.0 for category in CATEGORIES},
            }

        category = entry.get("category", "Unknown")
        amount = normalize_amount(entry.get("amount", 0.0)) or 0.0
        grouped[month_key]["totals"][category] = grouped[month_key]["totals"].get(category, 0.0) + amount

    summary = []
    for month_key in sorted(grouped.keys()):
        totals = grouped[month_key]["totals"]
        total_rows = ordered_totals(totals)
        summary.append(
            {
                "month_label": grouped[month_key]["month_label"],
                "totals": total_rows,
                "month_total": sum(item["amount"] for item in total_rows),
            }
        )
    return summary


def build_monthly_chart_data(monthly_rows):
    """Build chart labels and values for monthly trend visualization."""
    labels = [row["month_label"] for row in monthly_rows]
    values = [row["month_total"] for row in monthly_rows]
    return labels, values


@app.route("/", methods=["GET"])
def index():
    expenses = load_expenses()
    month_filter = request.args.get("month", "").strip()

    filtered_expenses, month_label, filter_error = filter_expenses_by_month(expenses, month_filter)
    if filtered_expenses is None:
        filtered_expenses = []

    expense_rows = []
    for entry in sorted_expenses_by_date(filtered_expenses):
        amount = normalize_amount(entry.get("amount", 0.0)) or 0.0
        expense_rows.append(
            {
                "id": entry.get("id", ""),
                "name": entry.get("name", "Untitled"),
                "category": entry.get("category", "Unknown"),
                "amount": amount,
                "date": entry.get("date", "N/A"),
            }
        )

    totals = build_totals_by_category(filtered_expenses)
    total_rows = ordered_totals(totals)
    total_spending = sum(item["amount"] for item in total_rows)

    all_monthly_summary = monthly_summary(expenses)
    monthly_chart_labels, monthly_chart_values = build_monthly_chart_data(all_monthly_summary)

    return render_template(
        "index.html",
        app_title=APP_TITLE,
        categories=CATEGORIES,
        expenses=expense_rows,
        totals=total_rows,
        total_spending=total_spending,
        month_label=month_label or "All Months",
        month_filter=month_filter,
        filter_error=filter_error,
        monthly_summary=all_monthly_summary,
        category_chart_labels=[row["category"] for row in total_rows],
        category_chart_values=[row["amount"] for row in total_rows],
        monthly_chart_labels=monthly_chart_labels,
        monthly_chart_values=monthly_chart_values,
    )

@app.route("/expenses", methods=["POST"])
def add_expense():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    amount_text = request.form.get("amount", "").strip()
    date_str = request.form.get("date", "").strip()
    month_filter = request.form.get("month", "").strip()

    if not name:
        flash("Expense name cannot be empty.", "error")
        return redirect_to_index(month_filter)

    if category not in CATEGORIES:
        flash("Please choose a valid category.", "error")
        return redirect_to_index(month_filter)

    amount = normalize_amount(amount_text)
    if amount is None:
        flash("Please enter a valid non-negative amount.", "error")
        return redirect_to_index(month_filter)

    if parse_date(date_str, DATE_FORMAT) is None:
        flash("Please use YYYY-MM-DD for the date.", "error")
        return redirect_to_index(month_filter)

    expenses = load_expenses()
    expenses.append(
        {
            "id": uuid4().hex,
            "name": name,
            "category": category,
            "amount": amount,
            "date": date_str,
        }
    )
    save_expenses(expenses)
    flash("Expense saved successfully.", "success")
    return redirect_to_index(month_filter)


@app.route("/expenses/<expense_id>/edit", methods=["POST"])
def edit_expense(expense_id):
    month_filter = request.form.get("month", "").strip()
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    amount_text = request.form.get("amount", "").strip()
    date_str = request.form.get("date", "").strip()

    if not name:
        flash("Expense name cannot be empty.", "error")
        return redirect_to_index(month_filter)

    if category not in CATEGORIES:
        flash("Please choose a valid category.", "error")
        return redirect_to_index(month_filter)

    amount = normalize_amount(amount_text)
    if amount is None:
        flash("Please enter a valid non-negative amount.", "error")
        return redirect_to_index(month_filter)

    if parse_date(date_str, DATE_FORMAT) is None:
        flash("Please use YYYY-MM-DD for the date.", "error")
        return redirect_to_index(month_filter)

    expenses = load_expenses()
    entry_index = find_expense_index(expenses, expense_id)
    if entry_index == -1:
        flash("Expense not found.", "error")
        return redirect_to_index(month_filter)

    expenses[entry_index].update(
        {
            "name": name,
            "category": category,
            "amount": amount,
            "date": date_str,
        }
    )
    save_expenses(expenses)
    flash("Expense updated.", "success")
    return redirect_to_index(month_filter)


@app.route("/expenses/<expense_id>/delete", methods=["POST"])
def delete_expense(expense_id):
    month_filter = request.form.get("month", "").strip()
    expenses = load_expenses()
    entry_index = find_expense_index(expenses, expense_id)

    if entry_index == -1:
        flash("Expense not found.", "error")
        return redirect_to_index(month_filter)

    del expenses[entry_index]
    save_expenses(expenses)
    flash("Expense deleted.", "success")
    return redirect_to_index(month_filter)


if __name__ == "__main__":
    app.run(debug=True)
