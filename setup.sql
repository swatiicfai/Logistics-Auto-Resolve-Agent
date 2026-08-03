-- setup.sql
-- Run this entire script in a Snowflake SQL Worksheet

-- 1. Create a database and schema for our hackathon project
CREATE DATABASE IF NOT EXISTS SUPPLY_CHAIN_DB;
USE DATABASE SUPPLY_CHAIN_DB;
CREATE SCHEMA IF NOT EXISTS LOGISTICS;
USE SCHEMA LOGISTICS;

-- 2. Create the Shipments table
CREATE OR REPLACE TABLE SHIPMENTS (
    SHIPMENT_ID VARCHAR(50),
    ORIGIN VARCHAR(100),
    DESTINATION VARCHAR(100),
    PRODUCT_ID VARCHAR(50),
    QUANTITY INT,
    STATUS VARCHAR(50),
    EXPECTED_ARRIVAL DATE
);

-- 3. Insert mock shipment data
INSERT INTO SHIPMENTS (SHIPMENT_ID, ORIGIN, DESTINATION, PRODUCT_ID, QUANTITY, STATUS, EXPECTED_ARRIVAL)
VALUES 
    ('SHP-4092', 'Port of Los Angeles', 'New York Distribution Center', 'PROD-A1', 1000, 'In Transit', '2026-08-10'),
    ('SHP-8812', 'Shenzhen', 'Seattle Warehouse', 'PROD-B2', 500, 'Delayed', '2026-08-15');

-- 4. Create the Inventory table
CREATE OR REPLACE TABLE INVENTORY (
    WAREHOUSE VARCHAR(100),
    PRODUCT_ID VARCHAR(50),
    CURRENT_STOCK INT,
    MINIMUM_REQUIRED INT
);

-- 5. Insert mock inventory data
INSERT INTO INVENTORY (WAREHOUSE, PRODUCT_ID, CURRENT_STOCK, MINIMUM_REQUIRED)
VALUES 
    ('New York Distribution Center', 'PROD-A1', 200, 500),
    ('Texas Regional Warehouse', 'PROD-A1', 2500, 1000),
    ('Seattle Warehouse', 'PROD-B2', 50, 100);

-- Verify the data was inserted correctly
SELECT * FROM SHIPMENTS;
SELECT * FROM INVENTORY;
