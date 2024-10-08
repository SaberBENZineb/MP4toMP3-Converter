-- Drop the user if it already exists
DROP USER IF EXISTS 'auth_user'@'%';

-- Create the user with a specified password
CREATE USER 'auth_user'@'%' IDENTIFIED BY 'password';

-- Create the database if it does not already exist
CREATE DATABASE IF NOT EXISTS auth;

-- Grant all privileges on the database to the user
GRANT ALL PRIVILEGES ON auth.* TO 'auth_user'@'%';

-- Flush privileges to ensure changes take effect
FLUSH PRIVILEGES;

-- Use the newly created database
USE auth;

-- Create the user table with specified columns
CREATE TABLE user (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Insert a sample user into the user table
INSERT INTO user (email, password) VALUES (
    "admin@email.com",
    "Admin"
);
