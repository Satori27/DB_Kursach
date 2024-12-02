CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE employee (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE organization_type AS ENUM (
    'IE',
    'LLC',
    'JSC'
);

CREATE TABLE organization (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    type organization_type,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE organization_responsible (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organization(id) ON DELETE CASCADE,
    user_id UUID REFERENCES employee(id) ON DELETE CASCADE
);



CREATE TABLE IF NOT EXISTS  tenders(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Created',
    employee_username VARCHAR(50) NOT NULL,
    FOREIGN KEY (employee_username) REFERENCES employee(username),
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS tender_versions(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tender_id UUID NOT NULL,
    FOREIGN KEY (tender_id) REFERENCES tenders(id),
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    employee_username VARCHAR(50) NOT NULL,
    FOREIGN KEY (employee_username) REFERENCES employee(username),
    version INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bids(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Created',
    tender_id UUID NOT NULL,
    FOREIGN KEY (tender_id) REFERENCES tenders(id),
    employee_username VARCHAR(50) NOT NULL,
    FOREIGN KEY (employee_username) REFERENCES employee(username),
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bid_versions(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Created',
    tender_id UUID NOT NULL,
    FOREIGN KEY (tender_id) REFERENCES tenders(id),
    bid_id UUID NOT NULL,
    FOREIGN KEY (bid_id) REFERENCES bids(id),
    employee_username VARCHAR(50) NOT NULL,
    FOREIGN KEY (employee_username) REFERENCES employee(username),
    version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);


CREATE TABLE IF NOT EXISTS bid_feedback(
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feedback TEXT NOT NULL,
    bid_id UUID NOT NULL,
    FOREIGN KEY (bid_id) REFERENCES bids(id),
    employee_username VARCHAR(50) NOT NULL,
    FOREIGN KEY (employee_username) REFERENCES employee(username),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);



CREATE TYPE tender_status AS ENUM (
    'Created',
    'Published',
    'Closed'
);

CREATE TYPE bid_status AS ENUM (
    'Created',
    'Published',
    'Canceled',
    'Approved',
    'Rejected'
);


INSERT INTO organization(name, description, type)
VALUES('org1', 'desc1', 'IE');

INSERT INTO organization(name, description, type)
VALUES('org2', 'desc2', 'LLC');
