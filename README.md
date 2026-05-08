# 🎓 UNIPOCKET – Spend Wise, Save Smart
> Student Finance Tracker | DBMS Project | MIT-WPU

---

## 📁 Project Structure
```
unipocket/
├── index.html        ← Frontend (single file, works standalone too)
├── app.py            ← Flask backend
├── schema.sql        ← MySQL database setup
├── requirements.txt  ← Python packages
└── README.md
```

---

## ⚡ DAY 1 SETUP (Backend + DB)

### Step 1 — MySQL Setup
```bash
mysql -u root -p
SOURCE schema.sql;
```

### Step 2 — Python Backend
```bash
cd unipocket
pip install -r requirements.txt

# Edit app.py line 20: change DB password
# DB_CONFIG = { ..., "password": "YOUR_MYSQL_PASSWORD" }

python app.py
# Flask runs on http://localhost:5000
```

---

## 🎨 DAY 2 SETUP (Frontend)

### Option A — Open directly in browser (Demo Mode)
Just double-click `index.html` — works fully with mock data!
No backend needed for demo/hackathon.

### Option B — Connect to Flask backend
Make sure Flask is running on port 5000, then open `index.html`.
The frontend auto-detects the backend.

---

## 🚀 Deploy to Railway (Free)

1. Push to GitHub
2. Go to railway.app → New Project → Deploy from GitHub
3. Add MySQL plugin
4. Set environment variable: `MYSQL_URL`
5. Done! Live URL in minutes.

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/register | Register new student |
| POST | /api/login | Login |
| GET  | /api/dashboard/:stu_id | Dashboard data |
| POST | /api/expense | Add expense |
| GET  | /api/expense/:acc_id | Get all expenses |
| POST | /api/income | Add income |
| GET  | /api/income/:acc_id | Get all income |
| GET  | /api/categories | Get categories |

---

## 🔑 Demo Credentials
- Email: `pooja@mitwpu.edu.in`
- Password: `pooja123`

---

## 🧠 ER Diagram Entities Implemented
- ✅ STUDENT
- ✅ ACCOUNT (owns relationship)
- ✅ EXPENSE (records relationship)
- ✅ INCOME (receives relationship)
- ✅ CATEGORY (classify relationship)
- ✅ ALERT (trigger relationship)
