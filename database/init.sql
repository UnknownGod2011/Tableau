-- TreasuryIQ Database Initialization Script
-- Creates initial database structure and demo data

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
CREATE TYPE currency_code AS ENUM (
    'USD', 'EUR', 'GBP', 'JPY', 'SGD', 'AUD', 'CAD', 'CHF', 'CNY', 'HKD'
);

CREATE TYPE risk_level AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

CREATE TYPE entity_type AS ENUM ('HEADQUARTERS', 'SUBSIDIARY', 'DIVISION', 'BRANCH');

CREATE TYPE account_type AS ENUM (
    'CHECKING', 'SAVINGS', 'MONEY_MARKET', 'CD', 'TREASURY', 'INVESTMENT'
);

CREATE TYPE investment_type AS ENUM (
    'TREASURY_BILL', 'CORPORATE_BOND', 'MONEY_MARKET_FUND', 'CD', 'COMMERCIAL_PAPER'
);

CREATE TYPE alert_type AS ENUM (
    'CASH_OPTIMIZATION', 'RISK_THRESHOLD', 'LIQUIDITY_WARNING', 'SUPPLIER_RISK', 'MARKET_VOLATILITY'
);

CREATE TYPE notification_channel AS ENUM ('EMAIL', 'SLACK', 'SMS', 'MOBILE_PUSH');

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create tables will be handled by SQLAlchemy migrations
-- This script focuses on initial setup and demo data

-- Insert demo data for GlobalTech Industries
-- This will be populated by the application during startup