CREATE DATABASE IF NOT EXISTS unipocket;
USE unipocket;


-- 1. Student Table
CREATE TABLE student (
    stu_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- 2. Account Table
CREATE TABLE account (
    acc_id INT AUTO_INCREMENT PRIMARY KEY,
    stu_id VARCHAR(20),
    curr_balance DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (stu_id) REFERENCES student(stu_id) ON DELETE CASCADE
);

-- 3. Category Table
CREATE TABLE category (
    cat_id INT AUTO_INCREMENT PRIMARY KEY,
    cat_name VARCHAR(50),
    budget DECIMAL(10, 2)
);

-- 4. Expense Table
CREATE TABLE expense (
    exp_id INT AUTO_INCREMENT PRIMARY KEY,
    acc_id INT,
    cat_id INT,
    amount DECIMAL(10, 2),
    note VARCHAR(255),
    exp_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (acc_id) REFERENCES account(acc_id) ON DELETE CASCADE,
    FOREIGN KEY (cat_id) REFERENCES category(cat_id)
);
-- 8. Income Table
CREATE TABLE IF NOT EXISTS income (
    inc_id INT AUTO_INCREMENT PRIMARY KEY,
    acc_id INT,
    amount DECIMAL(10, 2),
    source VARCHAR(255),
    inc_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (acc_id) REFERENCES account(acc_id) ON DELETE CASCADE
);

-- 5. Insert Default Categories
INSERT IGNORE INTO category (cat_id, cat_name, budget) VALUES 
(1, 'Food', 5000.00),
(2, 'Travel', 2000.00),
(3, 'College', 3000.00),
(4, 'Shopping', 4000.00),
(5, 'Others', 1500.00);

-- 6. Trigger: Update balance when expense is added
DELIMITER //
CREATE TRIGGER UpdateBalanceAfterExpense
AFTER INSERT ON expense
FOR EACH ROW
BEGIN
    UPDATE account 
    SET curr_balance = curr_balance - NEW.amount
    WHERE acc_id = NEW.acc_id;
END //

-- 7. Trigger: Restore balance when expense is deleted
CREATE TRIGGER RestoreBalanceAfterDelete
AFTER DELETE ON expense
FOR EACH ROW
BEGIN
    UPDATE account 
    SET curr_balance = curr_balance + OLD.amount
    WHERE acc_id = OLD.acc_id;
END //

DELIMITER ;


DELIMITER //
-- 9. Trigger: Update balance when income is added
CREATE TRIGGER UpdateBalanceAfterIncome
AFTER INSERT ON income
FOR EACH ROW
BEGIN
    UPDATE account 
    SET curr_balance = curr_balance + NEW.amount
    WHERE acc_id = NEW.acc_id;
END //
-- Updates balance when you spend money
CREATE TRIGGER UpdateBalanceAfterExpense
AFTER INSERT ON expense
FOR EACH ROW
BEGIN
    UPDATE account 
    SET curr_balance = curr_balance - NEW.amount
    WHERE acc_id = NEW.acc_id;
END //
DELIMITER ;

-- 10. Trigger: Restore balance when income is deleted
CREATE TRIGGER RestoreBalanceAfterIncomeDelete
AFTER DELETE ON income
FOR EACH ROW
BEGIN
    UPDATE account 
    SET curr_balance = curr_balance - OLD.amount
    WHERE acc_id = OLD.acc_id;
END //

-- 11. Trigger: Before spending (Check sufficient balance)
CREATE TRIGGER BeforeSpending
BEFORE INSERT ON expense
FOR EACH ROW
BEGIN
    DECLARE current_bal DECIMAL(10,2);
    SELECT curr_balance INTO current_bal FROM account WHERE acc_id = NEW.acc_id;
    IF current_bal < NEW.amount THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient balance for this expense';
    END IF;
END //

/*-- 12. Trigger: Before Update on expense
CREATE TRIGGER CheckExpenseBeforeUpdate
BEFORE UPDATE ON expense
FOR EACH ROW
BEGIN
    DECLARE current_bal DECIMAL(10,2);
    IF NEW.amount <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Expense amount must be positive';
    END IF;
    SELECT curr_balance INTO current_bal FROM account WHERE acc_id = NEW.acc_id;
    IF (current_bal + OLD.amount) < NEW.amount THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient balance for this updated expense';
    END IF;
END //
*/

-- 13. Trigger: After Update on expense
CREATE TRIGGER UpdateBalanceAfterExpenseUpdate
AFTER UPDATE ON expense
FOR EACH ROW
BEGIN
    UPDATE account 
    SET curr_balance = curr_balance + OLD.amount - NEW.amount
    WHERE acc_id = NEW.acc_id;
END //

-- 14. Trigger: Before Update on income
CREATE TRIGGER CheckIncomeBeforeUpdate
BEFORE UPDATE ON income
FOR EACH ROW
BEGIN
    IF NEW.amount <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Income amount must be positive';
    END IF;
END //

-- 15. Trigger: After Update on income
CREATE TRIGGER UpdateBalanceAfterIncomeUpdate
AFTER UPDATE ON income
FOR EACH ROW
BEGIN
    UPDATE account 
    SET curr_balance = curr_balance - OLD.amount + NEW.amount
    WHERE acc_id = NEW.acc_id;
END //

-- 16. Function: Get the total expenses of an account
CREATE FUNCTION GetTotalExpenses(accID INT) 
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(10,2);
    SELECT COALESCE(SUM(amount), 0.00) INTO total FROM expense WHERE acc_id = accID;
    RETURN total;
END //

-- 17. Function: Get the total income of an account
CREATE FUNCTION GetTotalIncome(accID INT) 
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(10,2);
    SELECT COALESCE(SUM(amount), 0.00) INTO total FROM income WHERE acc_id = accID;
    RETURN total;
END //

DELIMITER ;
