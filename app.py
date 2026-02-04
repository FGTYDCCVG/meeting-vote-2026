!pip install flask
import sqlite3
from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)

OPTIONS = ["14:00", "15:00", "16:00", "17:00", "18:00"]
DB = "votes.db"

# --- работа с базой ---
def get_db():
    return sqlite3.connect(DB)

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                time TEXT PRIMARY KEY,
                count INTEGER
            )
        """)
        for o in OPTIONS:
            conn.execute(
                "INSERT OR IGNORE INTO votes (time, count) VALUES (?, 0)", (o,)
            )

def get_votes():
    with get_db() as conn:
        rows = conn.execute("SELECT time, count FROM votes").fetchall()
    return dict(rows)

def add_votes(selected):
    with get_db() as conn:
        for t in selected:
            conn.execute(
                "UPDATE votes SET count = count + 1 WHERE time = ?", (t,)
            )

def reset_votes():
    with get_db() as conn:
        conn.execute("UPDATE votes SET count = 0")

# --- HTML ---
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Голосование</title>
</head>
<body>
    <h2>Выберите удобное время начала встречи 06.02.2026</h2>

    <form method="post">
        {% for o in options %}
            <input type="checkbox" name="time" value="{{o}}">
            {{o}}<br>
        {% endfor %}
        <br>
        <button type="submit">Проголосовать</button>
    </form>

    <br>

    <form method="post" action="/reset">
        <button type="submit">Обнулить результаты</button>
    </form>

    <hr>

    <h3>Результаты:</h3>
    {% for o, c in votes.items() %}
        {{o}} — {{c}}<br>
    {% endfor %}
</body>
</html>
"""

# --- маршруты ---
@app.route("/", methods=["GET", "POST"])
def vote():
    if request.method == "POST":
        selected = request.form.getlist("time")
        add_votes(selected)
        return redirect(url_for("vote"))

    return render_template_string(
        HTML,
        options=OPTIONS,
        votes=get_votes()
    )

@app.route("/reset", methods=["POST"])
def reset():
    reset_votes()
    return redirect(url_for("vote"))

# --- запуск ---
init_db()
app.run(host="127.0.0.2", port=5000, debug=False, use_reloader=False)