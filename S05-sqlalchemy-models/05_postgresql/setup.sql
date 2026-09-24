-- Create the user and the database of the course (run once, as the "postgres" superuser).
--   Windows:  psql -U postgres -f setup.sql
--   Ubuntu:   sudo -u postgres psql < setup.sql
CREATE ROLE training WITH LOGIN PASSWORD 'training';
CREATE DATABASE training OWNER training;
