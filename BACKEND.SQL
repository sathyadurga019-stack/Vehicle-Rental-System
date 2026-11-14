CREATE DATABASE IF NOT EXISTS vehicle_rental_system;

USE vehicle_rental_system;

-- 1. Branch Table
CREATE TABLE IF NOT EXISTS Branch (
    Branch_ID INT PRIMARY KEY,
    Branch_Name VARCHAR(100),
    Location VARCHAR(100),
    Phone VARCHAR(15),
    Manager_Name VARCHAR(100)
);

-- 2. Customer Table
CREATE TABLE IF NOT EXISTS Customer (
    Customer_ID INT PRIMARY KEY,
    Name VARCHAR(100),
    Phone VARCHAR(15),
    Email VARCHAR(100),
    Address VARCHAR(200),
    License_No VARCHAR(50)
);

-- 3. Vehicle Table
CREATE TABLE IF NOT EXISTS Vehicle (
    Vehicle_ID INT PRIMARY KEY,
    Vehicle_Number VARCHAR(20),
    Brand VARCHAR(50),
    Model VARCHAR(50),
    Vehicle_Type VARCHAR(50),
    Daily_Rate DECIMAL(10,2),
    Status VARCHAR(30),
    Branch_ID INT,
    FOREIGN KEY (Branch_ID) REFERENCES Branch(Branch_ID)
);

-- 4. Employee Table
CREATE TABLE IF NOT EXISTS Employee (
    Employee_ID INT PRIMARY KEY,
    Name VARCHAR(100),
    Phone VARCHAR(15),
    Email VARCHAR(100),
    Role VARCHAR(50),
    Branch_ID INT,
    FOREIGN KEY (Branch_ID) REFERENCES Branch(Branch_ID)
);

-- 5. Booking Table
CREATE TABLE IF NOT EXISTS Booking (
    Booking_ID INT PRIMARY KEY,
    Customer_ID INT,
    Vehicle_ID INT,
    Booking_Date DATE,
    Pickup_Date DATE,
    Return_Date DATE,
    Total_Amount DECIMAL(10,2),
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID),
    FOREIGN KEY (Vehicle_ID) REFERENCES Vehicle(Vehicle_ID)
);

-- 6. Payment Table
CREATE TABLE IF NOT EXISTS Payment (
    Payment_ID INT PRIMARY KEY,
    Booking_ID INT,
    Payment_Date DATE,
    Amount DECIMAL(10,2),
    Payment_Method VARCHAR(30),
    Payment_Status VARCHAR(30),
    Transaction_ID VARCHAR(50),
    FOREIGN KEY (Booking_ID) REFERENCES Booking(Booking_ID)
);

-- 7. Return Table
CREATE TABLE IF NOT EXISTS `Return` (
    Return_ID INT PRIMARY KEY,
    Booking_ID INT,
    Return_Date DATE,
    Vehicle_Condition VARCHAR(100),
    Late_Fee DECIMAL(10,2),
    Remarks VARCHAR(200),
    FOREIGN KEY (Booking_ID) REFERENCES Booking(Booking_ID)
);

-- 8. Maintenance Table
CREATE TABLE IF NOT EXISTS Maintenance (
    Maintenance_ID INT PRIMARY KEY,
    Vehicle_ID INT,
    Service_Date DATE,
    Service_Type VARCHAR(50),
    Cost DECIMAL(10,2),
    Description VARCHAR(200),
    FOREIGN KEY (Vehicle_ID) REFERENCES Vehicle(Vehicle_ID)
);

-- Display Tables
SHOW TABLES;

-- Basic SELECT Queries
SELECT * FROM Branch;
SELECT * FROM Customer;
SELECT * FROM Vehicle;
SELECT * FROM Employee;
SELECT * FROM Booking ORDER BY Booking_Date;
SELECT * FROM Payment;
SELECT * FROM `Return`;
SELECT * FROM Maintenance;

-- Vehicle Queries
SELECT * FROM Vehicle
WHERE Status = 'Available';

SELECT * FROM Vehicle
WHERE Status = 'Maintenance';

SELECT * FROM Vehicle
WHERE Daily_Rate > 2000;

-- Customer Queries
SELECT Customer_ID, Name, Email
FROM Customer
WHERE Email IS NOT NULL;

-- Join Queries
SELECT v.Vehicle_Number, v.Brand, v.Model, b.Branch_Name
FROM Vehicle v
JOIN Branch b ON v.Branch_ID = b.Branch_ID;

SELECT e.Name, e.Role, b.Branch_Name
FROM Employee e
JOIN Branch b ON e.Branch_ID = b.Branch_ID;

SELECT b.Booking_ID, c.Name, v.Vehicle_Number,
       b.Pickup_Date, b.Return_Date, b.Total_Amount
FROM Booking b
JOIN Customer c ON b.Customer_ID = c.Customer_ID
JOIN Vehicle v ON b.Vehicle_ID = v.Vehicle_ID;

SELECT p.Payment_ID, p.Booking_ID, p.Amount,
       p.Payment_Method, p.Payment_Status
FROM Payment p
JOIN Booking b ON p.Booking_ID = b.Booking_ID;

SELECT m.Maintenance_ID, v.Vehicle_Number,
       m.Service_Type, m.Cost, m.Service_Date
FROM Maintenance m
JOIN Vehicle v ON m.Vehicle_ID = v.Vehicle_ID;

-- Aggregate Queries
SELECT COUNT(*) AS Total_Customers
FROM Customer;

SELECT COUNT(*) AS Total_Vehicles
FROM Vehicle;

SELECT COUNT(*) AS Available_Vehicles
FROM Vehicle
WHERE Status = 'Available';

SELECT AVG(Daily_Rate) AS Average_Daily_Rate
FROM Vehicle;

SELECT MAX(Daily_Rate) AS Maximum_Daily_Rate
FROM Vehicle;

SELECT MIN(Daily_Rate) AS Minimum_Daily_Rate
FROM Vehicle;

SELECT SUM(Total_Amount) AS Total_Booking_Amount
FROM Booking;

SELECT SUM(Amount) AS Total_Payment_Amount
FROM Payment;

-- GROUP BY Queries
SELECT Vehicle_Type, COUNT(*) AS Vehicle_Count
FROM Vehicle
GROUP BY Vehicle_Type;

SELECT Status, COUNT(*) AS Vehicle_Count
FROM Vehicle
GROUP BY Status;

SELECT Branch_ID, COUNT(*) AS Vehicle_Count
FROM Vehicle
GROUP BY Branch_ID;

-- HAVING Query
SELECT Branch_ID, COUNT(*) AS Vehicle_Count
FROM Vehicle
GROUP BY Branch_ID
HAVING COUNT(*) > 1;
