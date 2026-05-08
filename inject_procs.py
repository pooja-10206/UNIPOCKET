import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "pooja", 
    "database": "unipocket"
}

db = mysql.connector.connect(**DB_CONFIG)
cur = db.cursor()

# Clean up any existing procedures just to be safe before recreating them
try:
    cur.execute("DROP PROCEDURE IF EXISTS RegisterStudentProc")
    cur.execute("DROP PROCEDURE IF EXISTS AddExpenseProc")
    cur.execute("DROP PROCEDURE IF EXISTS AddIncomeProc")
    cur.execute("DROP PROCEDURE IF EXISTS DeleteExpenseProc")
    cur.execute("DROP PROCEDURE IF EXISTS DeleteIncomeProc")
except:
    pass

procs = [
"""
CREATE PROCEDURE RegisterStudentProc(
    IN p_stu_id VARCHAR(20),
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_password VARCHAR(255)
)
BEGIN
    INSERT INTO student (stu_id, name, email, password) VALUES (p_stu_id, p_name, p_email, p_password);
    INSERT INTO account (stu_id, curr_balance) VALUES (p_stu_id, 1000.00);
END
""",
"""
CREATE PROCEDURE AddExpenseProc(
    IN p_acc_id INT,
    IN p_cat_id INT,
    IN p_amount DECIMAL(10, 2),
    IN p_note VARCHAR(255)
)
BEGIN
    INSERT INTO expense (acc_id, cat_id, amount, note) 
    VALUES (p_acc_id, p_cat_id, p_amount, p_note);
END
""",
"""
CREATE PROCEDURE AddIncomeProc(
    IN p_acc_id INT,
    IN p_amount DECIMAL(10, 2),
    IN p_source VARCHAR(255)
)
BEGIN
    INSERT INTO income (acc_id, amount, source) 
    VALUES (p_acc_id, p_amount, p_source);
END
""",
"""
CREATE PROCEDURE DeleteExpenseProc(
    IN p_exp_id INT
)
BEGIN
    DELETE FROM expense WHERE exp_id = p_exp_id;
END
""",
"""
CREATE PROCEDURE DeleteIncomeProc(
    IN p_inc_id INT
)
BEGIN
    DELETE FROM income WHERE inc_id = p_inc_id;
END
"""
]

for p in procs:
    try:
        cur.execute(p)
        print("Successfully created procedure.")
    except Exception as e:
        print("Error creating procedure:", e)

db.commit()
cur.close()
db.close()
print("All procedures injected successfully!")
