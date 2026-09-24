# PostgreSQL on your own computer (Windows 11 and Ubuntu)

SQLite is a file and needs nothing. PostgreSQL is a real database **server**:
it runs in the background as a service and programs connect to it over the
network (here: `localhost`, port `5432`). Install it once; every later
session can use it by changing only `DATABASE_URL`.

## 1. Install

### Windows 11
Open **PowerShell** and run:
```powershell
winget install --id PostgreSQL.PostgreSQL.17
```
(or download the installer from <https://www.postgresql.org/download/windows/>).

The installer asks for:
* a password for the superuser **`postgres`**: write it down, you need it in step 2;
* the port: keep **5432**;
* the components: keep *PostgreSQL Server*, *pgAdmin 4* (a graphical tool) and
  *Command Line Tools*.

PostgreSQL now runs as a Windows service called `postgresql-x64-17` and starts
with Windows. To use `psql` in a terminal, add its folder to `PATH` (once),
then open a **new** terminal:
```powershell
setx PATH "$env:PATH;C:\Program Files\PostgreSQL\17\bin"
```

### Ubuntu (22.04 / 24.04)
```bash
sudo apt update
sudo apt install postgresql
sudo systemctl enable --now postgresql    # start now and at every boot
systemctl status postgresql               # should say "active"
```
Ubuntu creates the superuser `postgres` without a password; you use it through
`sudo -u postgres`.

## 2. Create the course user and database
In this folder:
```bash
psql -U postgres -f setup.sql             # Windows (asks the postgres password)
sudo -u postgres psql < setup.sql         # Ubuntu
```
This creates the user `training` (password `training`) and the database
`training`. The connection URL for the course is therefore:
```
postgresql+psycopg://training:training@localhost:5432/training
```

## 3. Run the example
```bash
python app.py
```
It creates a table, inserts a row and prints `postgresql -> [(1, 'FastAPI')]`.

## Everyday commands
| Task | Windows (PowerShell as admin) | Ubuntu |
|------|-------------------------------|--------|
| Is it running? | `Get-Service postgresql*` | `systemctl status postgresql` |
| Start | `net start postgresql-x64-17` | `sudo systemctl start postgresql` |
| Stop | `net stop postgresql-x64-17` | `sudo systemctl stop postgresql` |
| Open a SQL shell | `psql -U training -d training -h localhost` | `psql -U training -d training -h localhost` |
| Delete all course data | `psql -U postgres -c "DROP DATABASE training"` then step 2 | `sudo -u postgres psql -c "DROP DATABASE training"` then step 2 |

Inside `psql`: `\dt` lists the tables, `\d courses` describes one, `\q` quits.

## Using PostgreSQL in the later projects
Put the URL in the project's `.env`:
```
DATABASE_URL=postgresql+psycopg://training:training@localhost:5432/training     # sessions 05-11 (sync)
DATABASE_URL=postgresql+asyncpg://training:training@localhost:5432/training     # session 12 and later (async)
```
and run `alembic upgrade head` (from session 8) and `python seed.py` as usual.
To give each session a clean database, create more databases, for example
`CREATE DATABASE training_s08 OWNER training;`, and use that name in the URL.
