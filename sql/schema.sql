-- Star schema for the E-Commerce Lieferkette & Retouren analysis.
-- SQLite dialect (no server required, easy for anyone to reproduce).

DROP TABLE IF EXISTS Fact_Orders;
DROP TABLE IF EXISTS Dim_Customers;
DROP TABLE IF EXISTS Dim_Products;

CREATE TABLE Dim_Customers (
    CustomerID  TEXT PRIMARY KEY,
    PLZ         TEXT,
    City        TEXT,
    State       TEXT
);

CREATE TABLE Dim_Products (
    ProductID    TEXT PRIMARY KEY,
    Category     TEXT NOT NULL,
    ProductName  TEXT NOT NULL,
    Price_EUR    REAL NOT NULL,
    Cost_EUR     REAL NOT NULL
);

CREATE TABLE Fact_Orders (
    OrderID             TEXT PRIMARY KEY,
    OrderDate           TEXT NOT NULL,
    DeliveryDate        TEXT NOT NULL,
    CustomerID          TEXT NOT NULL,
    ProductID           TEXT NOT NULL,
    LogisticsProvider   TEXT NOT NULL,
    ShippingCost_EUR    REAL NOT NULL,
    IsReturned          INTEGER NOT NULL,
    ReturnReason        TEXT,
    FOREIGN KEY (CustomerID) REFERENCES Dim_Customers (CustomerID),
    FOREIGN KEY (ProductID) REFERENCES Dim_Products (ProductID)
);
