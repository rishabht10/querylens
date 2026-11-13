
# QueryLens

**Ask your database a question in plain English and get back the SQL, the results, and a chart.**

QueryLens is a natural-language-to-SQL app with automatic graph generation. You type a question such as *"Total sales per product category"*, an LLM (Google Gemini) turns it into a SQL query, the query runs safely against the database, and the results appear as a table and, when the shape of the data suits it, as a chart. The sample database is the classic **Northwind** sales dataset (SQLite).

## To Run on your Local Machine

### Prerequisites

- Python 3.10 or newer
- API Key from Google AI Studio

### 1. Clone the repository

```bash
git clone https://github.com/rishabht10/querylens.git
cd querylens
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv


# Windows (cmd)
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install the requirements

```bash
pip install -r backend/requirements.txt
```

### 4. Create the `.env` file

Create a file named `.env` inside the **`backend/`** :

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_FALLBACK_MODEL=gemini-2.5-flash-lite
```

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Your Google Gemini API key |
| `GEMINI_MODEL` | Yes | Primary model used to generate SQL |
| `GEMINI_FALLBACK_MODEL` | No | Tried if the primary model is overloaded (429/5xx errors) |

Check Google AI Studio for the current model. `.env` is listed in `.gitignore`

### 5. Start the server

Run this from the `backend` folder

```bash
cd backend
uvicorn main:app --reload
```

### 6. Open the app

Go to **http://127.0.0.1:8000** and ask a question.

## Features

- **Plain English to SQL** using the Google Gemini API.
- **Automatic charts**: the backend inspects the result and picks a bar chart (categories), a line chart (dates and time series) or a scatter plot (two numeric columns), rendered with Chart.js.
- **Schema-aware prompting**: table definitions, foreign keys and sample rows are read from the database and sent to the model, so it uses real table and column names.
- **Self-correcting**: if the generated SQL fails, the error is sent back to the model for a corrected query (up to 2 retries).
- **Model fallback**: if the primary Gemini model is overloaded, an optional fallback model is tried, with exponential back-off.
- **Command-line mode** for quick queries without the browser.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| LLM | Google Gemini (`google-genai`) |
| Database | SQLite (Northwind), SQLAlchemy for schema introspection |
| Frontend | HTML, CSS, vanilla JavaScript, Chart.js |

## How It Works

```
Question ──> Schema + prompt ──> Gemini ──> SQL ──> Validate ──> Run (read-only SQLite)
                                              ^                         |
                                              └── error + retry <───────┤
                                                                        v
                                                       Table + auto-picked chart
```

1. The frontend sends the question to `POST /api/query`.
2. `schema.py` builds a text description of the database, and `prompt.py` wraps it in a system prompt with rules and examples.
3. `nl2sql.py` and `llm.py` ask Gemini for a single SQL query.
4. `runner.py` validates the query, executes it read-only, and retries with the error message if it fails.
5. `charts.py` recommends a chart type, and the frontend renders the table and chart.

## Project Structure

```
querylens/
├── backend/
│   ├── main.py            #FastAPI app, /api/query endpoint, serves the frontend
│   ├── llm.py             #Gemini client, retries and model fallback
│   ├── nl2sql.py          #Question to SQL generation
│   ├── prompt.py          #System prompt, dialect notes, few-shot examples
│   ├── schema.py          #Reads tables, foreign keys and sample rows
│   ├── runner.py          #SQL validation, safe execution, retry loop
│   ├── charts.py          #Chart type recommendation
│   ├── cli.py             #Run from terminal
│   ├── northwind.db       #Sample database used
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── ui.css
└── .gitignore
```



## Screenshots

**Bar chart: "Total sales per product category"**

<img width="1307" height="902" alt="Screenshot 2026-11-07 055637" src="https://github.com/user-attachments/assets/6882da0d-5b64-43b5-9580-92033ab993fd" />


**Line chart: "No. of order per month"**

<img width="1297" height="890" alt="Screenshot 2026-11-07 055857" src="https://github.com/user-attachments/assets/ab85f749-f13a-4b52-b222-b759719a47bc" />

**Table output for the same category-sales query**

<img width="1296" height="430" alt="Screenshot 2026-11-07 124014" src="https://github.com/user-attachments/assets/0131a899-6941-42a1-baa9-6d3027e56076" />


**Simple aggregate: "what are the total no. of employee"**

<img width="1307" height="475" alt="Screenshot 2026-11-07 124333" src="https://github.com/user-attachments/assets/88f306b7-ede5-4f22-abd9-ecf78be6c44c" />

**Other queries** 
<img width="1301" height="525" alt="Screenshot 2026-11-07 124432" src="https://github.com/user-attachments/assets/1ef9bcb8-39dc-4ab5-aa3c-2f482bd9df37" /> 

<img width="1317" height="781" alt="Screenshot 2026-11-07 124559" src="https://github.com/user-attachments/assets/7c167009-f088-41c1-8a09-9f99fd6e1ec9" />
<img width="1432" height="1065" alt="Screenshot 2026-11-07 124649" src="https://github.com/user-attachments/assets/47247aa3-4683-4780-ba2d-5e3917ae2a20" />


## Example Questions to try

- Top 10 customers by total order value
- Average order value by country

## Safety

Because an LLM writes the SQL, every query is checked before it runs:

- Only a single `SELECT` (or `WITH ... SELECT`) statement is allowed.
- Statements containing `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `ATTACH`, `PRAGMA` and similar keywords are blocked.
- The database is opened in **read-only mode**. 
- Queries time out after 5 seconds, and results are capped at 500 rows.
- If the question cannot be answered from the schema, the model returns `CANNOT_ANSWER` and instead of guessing.


## Future Improvements

- Support for uploading database as .csv or .db file
- UI improvement
- Login and authentication
- History feature
- Exporting result as .csv

