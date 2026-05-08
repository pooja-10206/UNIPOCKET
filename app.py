from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
import bcrypt
from datetime import date, datetime
import json
from decimal import Decimal

app = Flask(__name__)
app.secret_key = "unipocket_secret_2026"
CORS(app)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "pooja", 
    "database": "unipocket"
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def serial(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt()).decode()
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("INSERT INTO student (stu_id, name, email, password) VALUES (%s, %s, %s, %s)", (data["stu_id"], data["name"], data["email"], hashed))
        db.commit()
        return jsonify({"stu_id": data["stu_id"], "name": data["name"]}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        db.close()

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    db = get_db()
    cur = db.cursor(dictionary=True)
    query = """
        SELECT s.stu_id, s.name, s.password, a.acc_id 
        FROM student s
        JOIN account a ON s.stu_id = a.stu_id
        WHERE s.email = %s
    """
    cur.execute("SELECT * FROM student WHERE email = %s", (data["email"],))
    user = cur.fetchone()
    cur.close()
    db.close()
    if user and bcrypt.checkpw(data["password"].encode(), user["password"].encode()):
        return jsonify({"stu_id": user["stu_id"], "name": user["name"]})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/dashboard/<stu_id>")
def dashboard_data(stu_id):
    sort_param = request.args.get("sort", "date_desc")
    order_by = "e.exp_date DESC"
    if sort_param == "date_asc": order_by = "e.exp_date ASC"
    elif sort_param == "amount_desc": order_by = "e.amount DESC"
    elif sort_param == "amount_asc": order_by = "e.amount ASC"
    elif sort_param == "cat_name_asc": order_by = "c.cat_name ASC, e.exp_date DESC"

    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM account WHERE stu_id = %s", (stu_id,))
        acc = cur.fetchone()
        
        if not acc:
            cur.execute("INSERT INTO account (stu_id, curr_balance) VALUES (%s, 10000.00)", (stu_id,))
            db.commit()
            cur.execute("SELECT * FROM account WHERE stu_id = %s", (stu_id,))
            acc = cur.fetchone()
        
        cur.execute(f"""SELECT e.exp_id, e.amount, e.exp_date, e.note, c.cat_name 
                       FROM expense e JOIN category c ON e.cat_id = c.cat_id 
                       WHERE e.acc_id = %s ORDER BY {order_by}""", (acc["acc_id"],))
        expenses = cur.fetchall()

        cur.execute("""SELECT c.cat_id, c.cat_name, c.budget, COALESCE(SUM(e.amount), 0) as spent 
                       FROM category c LEFT JOIN expense e ON c.cat_id = e.cat_id AND e.acc_id = %s 
                       GROUP BY c.cat_id, c.cat_name, c.budget""", (acc["acc_id"],))
        budgets = cur.fetchall()

        cur.execute("""SELECT * FROM income WHERE acc_id = %s ORDER BY date DESC""", (acc["acc_id"],))
        incomes = cur.fetchall()
        
        cur.execute("""SELECT COALESCE(SUM(amount), 0) as spent FROM expense WHERE acc_id = %s AND exp_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)""", (acc["acc_id"],))
        tw_row = cur.fetchone()
        this_week = tw_row["spent"] if tw_row else 0
        
        cur.execute("""SELECT COALESCE(SUM(amount), 0) as spent FROM expense WHERE acc_id = %s AND exp_date >= DATE_SUB(CURDATE(), INTERVAL 14 DAY) AND exp_date < DATE_SUB(CURDATE(), INTERVAL 7 DAY)""", (acc["acc_id"],))
        lw_row = cur.fetchone()
        last_week = lw_row["spent"] if lw_row else 0

        return json.dumps({"account": acc, "expenses": expenses, "budgets": budgets, "incomes": incomes, "trend": {"this_week": this_week, "last_week": last_week}}, default=serial), 200, {"Content-Type": "application/json"}
    finally:
        cur.close()
        db.close()

@app.route("/api/income", methods=["POST"])
def add_income():
    data = request.get_json(force=True)
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("INSERT INTO income (acc_id, amount, source) VALUES (%s, %s, %s)", (data["acc_id"], data["amount"], data.get("source", "")))
        db.commit()
        return jsonify({"message": "Added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        db.close()

@app.route("/api/income/<int:inc_id>", methods=["DELETE"])
def delete_income(inc_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute("SELECT acc_id, amount FROM income WHERE inc_id = %s", (inc_id,))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE account SET curr_balance = curr_balance - %s WHERE acc_id = %s", (row["amount"], row["acc_id"]))
            cur.execute("DELETE FROM income WHERE inc_id = %s", (inc_id,))
        db.commit()
        return jsonify({"message": "Deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        db.close()

@app.route("/api/expense/<int:exp_id>", methods=["DELETE"])
def delete_expense(exp_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute("SELECT acc_id, cat_id, amount FROM expense WHERE exp_id = %s", (exp_id,))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE account SET curr_balance = curr_balance + %s WHERE acc_id = %s", (row["amount"], row["acc_id"]))
            cur.execute("UPDATE category SET remaining_amt = remaining_amt + %s WHERE cat_id = %s", (row["amount"], row["cat_id"]))
            cur.execute("DELETE FROM expense WHERE exp_id = %s", (exp_id,))
        db.commit()
        return jsonify({"message": "Deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        db.close()

@app.route("/api/expense", methods=["POST"])
def add_expense():
    data = request.get_json(force=True)
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("INSERT INTO expense (acc_id, cat_id, amount, note) VALUES (%s, %s, %s, %s)", (data["acc_id"], data["cat_id"], data["amount"], data.get("note", "")))
        db.commit()
        return jsonify({"message": "Added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        db.close()

@app.route("/api/categories")
def get_categories():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM category")
    res = cur.fetchall()
    cur.close()
    db.close()
    return jsonify(res)

@app.route("/api/category/<int:cat_id>/budget", methods=["PUT"])
def update_budget(cat_id):
    data = request.get_json(force=True)
    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("UPDATE category SET budget = %s, unit_budget = %s, remaining_amt = %s WHERE cat_id = %s", (data["budget"], data["budget"], data["budget"], cat_id))
        db.commit()
        return jsonify({"message": "Budget Updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        db.close()

if __name__ == "__main__":
    app.run(debug=True)