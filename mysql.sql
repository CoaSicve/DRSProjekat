CREATE DATABASE IF NOT EXISTS drs_users_db;

USE drs_users_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(80) NOT NULL,
    
    lastName VARCHAR(80) NOT NULL,
    
    dateOfBirth DATE,
    
    email VARCHAR(120) UNIQUE NOT NULL,

    role ENUM('USER', 'MANAGER', 'ADMIN') NOT NULL DEFAULT 'USER',

    password VARCHAR(255) NOT NULL,

	gender VARCHAR(20),
    
    state VARCHAR(50),
    
    street VARCHAR(100),
    
    number VARCHAR(20),
    
    accountBalance FLOAT NOT NULL DEFAULT 0,

    profileImage LONGTEXT NULL
);

CREATE DATABASE IF NOT EXISTS drs_flights_db;

USE drs_flights_db;

CREATE TABLE IF NOT EXISTS airlines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,
    country VARCHAR(50) NOT NULL
);

INSERT INTO airlines (name, code, country) VALUES
('Qatar Airways', '8979ASD090', 'Qatar'),
('Turkish Airlines', '123ASKUG23', 'Turkey'),
('Air Serbia', 'ASE4246HJI', 'Serbia'),
('Emirates', 'NUJS42108Z', 'United Arab Emirates');

CREATE TABLE IF NOT EXISTS flights (
    id INT AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(100) NOT NULL,

    airline_id INT NOT NULL,

    distance_km FLOAT NOT NULL,
    duration_minutes INT NOT NULL,

    departure_time DATETIME NOT NULL,
    departure_airport VARCHAR(100) NOT NULL,
    arrival_airport VARCHAR(100) NOT NULL,

    created_by_user_id INT NOT NULL,
    ticket_price FLOAT NOT NULL,

    status ENUM('PENDING', 'APPROVED', 'REJECTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED') NOT NULL DEFAULT 'PENDING',
    rejection_reason TEXT NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_flights_airline
        FOREIGN KEY (airline_id)
        REFERENCES airlines(id)
        ON DELETE CASCADE
);