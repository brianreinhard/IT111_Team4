# Team 4 Spending Tracker (Flask)

A local web-based spending tracker that lets users:

- Add expenses with name, category, amount, and date
- View saved expenses sorted by date
- Filter expenses by month
- See category totals and a total spending value
- View monthly summary cards
- Persist data to a local `expenses.json` file

## Tech Stack

- Python 3.x
- Flask
- HTML + CSS (responsive UI)

## Project Layout

- `app.py` Flask application
- `templates/index.html` main web page template
- `static/styles.css` application styling
- `requirements.txt` Python dependencies
- `expenses.json` generated automatically after first saved expense

## Run Locally

From the project root directory (`IT111_Team4`):

1. Create a virtual environment

```bash
python -m venv venv
```

2. Activate the virtual environment

macOS/Linux:

```bash
source venv/bin/activate
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Start the web app

```bash
python app.py
```

5. Open in browser

`http://127.0.0.1:5000/`
