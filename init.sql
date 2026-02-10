-- init.sql

CREATE DATABASE IF NOT EXISTS drs_users_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS drs_flights_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Optional: mali "signal" da je skripta prošla
SELECT 'Databases created successfully!' AS status;