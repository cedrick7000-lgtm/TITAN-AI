import os, sqlite3
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

DB_PATH = os.getenv("TITAN_DB", "titan.db")
app = FastAPI(title="TITAN AI Starter")
app.mount("/static", StaticFiles(directory="static"), name="static")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, details TEXT DEFAULT '',
            status TEXT DEFAULT 'planned', created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL, platform TEXT DEFAULT '',
            url TEXT DEFAULT '', pay TEXT DEFAULT '',
            eligibility TEXT DEFAULT '', risk TEXT DEFAULT 'unverified',
            status TEXT DEFAULT 'to_review', notes TEXT DEFAULT '',
            created_at TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL, amount REAL NOT NULL,
            currency TEXT DEFAULT 'USD', received INTEGER DEFAULT 0,
            date TEXT NOT NULL)""")
init_db()

def now():
    return datetime.now(timezone.utc).isoformat()

@app.get("/", response_class=HTMLResponse)
def home():
    with db() as c:
        tasks = c.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
        opps = c.execute("SELECT * FROM opportunities ORDER BY id DESC").fetchall()
        income = c.execute("SELECT * FROM income ORDER BY id DESC").fetchall()
        total = c.execute("SELECT COALESCE(SUM(amount),0) n FROM income WHERE received=1").fetchone()["n"]
    def esc(s):
        return str(s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")
    task_rows = "".join(f"<tr><td>{esc(t['title'])}</td><td>{esc(t['status'])}</td><td>{esc(t['details'])}</td></tr>" for t in tasks) or "<tr><td colspan='3'>No tasks yet.</td></tr>"
    opp_rows = "".join(f"<tr><td>{esc(o['title'])}</td><td>{esc(o['platform'])}</td><td>{esc(o['pay'])}</td><td>{esc(o['risk'])}</td><td>{esc(o['status'])}</td><td>{('<a target=_blank rel=noopener href='+chr(34)+esc(o['url'])+chr(34)+'>Open</a>') if o['url'].startswith(('https://','http://')) else ''}</td></tr>" for o in opps) or "<tr><td colspan='6'>No opportunities recorded. Add links you find and verify them.</td></tr>"
    income_rows = "".join(f"<tr><td>{esc(i['source'])}</td><td>{i['amount']:.2f} {esc(i['currency'])}</td><td>{'Received' if i['received'] else 'Expected'}</td><td>{esc(i['date'])}</td></tr>" for i in income) or "<tr><td colspan='4'>No income recorded.</td></tr>"
    html = Path("static/index.html").read_text()
    return (html.replace("{{TOTAL}}", f"{total:.2f}")
                .replace("{{TASK_ROWS}}", task_rows)
                .replace("{{OPP_ROWS}}", opp_rows)
                .replace("{{INCOME_ROWS}}", income_rows))

@app.post("/tasks")
def add_task(title: str = Form(...), details: str = Form("")):
    with db() as c:
        c.execute("INSERT INTO tasks(title,details,created_at) VALUES(?,?,?)", (title[:160], details[:2000], now()))
    return RedirectResponse("/", status_code=303)

@app.post("/opportunities")
def add_opportunity(title: str = Form(...), platform: str = Form(""), url: str = Form(""),
                    pay: str = Form(""), eligibility: str = Form(""), notes: str = Form("")):
    # New leads are unverified until a human checks the company, terms and Rwanda eligibility.
    with db() as c:
        c.execute("""INSERT INTO opportunities(title,platform,url,pay,eligibility,notes,created_at)
                     VALUES(?,?,?,?,?,?,?)""",
                  (title[:160], platform[:120], url[:500], pay[:120], eligibility[:300], notes[:2000], now()))
    return RedirectResponse("/", status_code=303)

@app.post("/income")
def add_income(source: str = Form(...), amount: float = Form(...), currency: str = Form("USD"),
               received: str = Form("no"), date: str = Form("")):
    if amount < 0:
        return HTMLResponse("Amount must be zero or greater.", status_code=400)
    with db() as c:
        c.execute("INSERT INTO income(source,amount,currency,received,date) VALUES(?,?,?,?,?)",
                  (source[:160], amount, currency[:8], 1 if received == "yes" else 0, date[:30] or now()[:10]))
    return RedirectResponse("/", status_code=303)

@app.get("/health")
def health():
    return {"ok": True, "service": "TITAN AI Starter"}
