# Shilengae Backend Setup

Welcome to the **Shilengae** backend repository. This file documents the development environment for this project. Shilengae Backend is implemented in [Python 3.7.0](https://www.python.org/downloads/release/python-370/).

## Installing Python, PIP and Virtualenv

1. Install Python [Python 3.7.0](https://www.python.org/downloads/release/python-370/) or later.
2. Check if pip is already installed with Python via `pip --version`. If not, [install it](https://pip.pypa.io/en/stable/installing/).
3. [Install git](https://git-scm.com/download/) if not already installed (check with `git --version`).
4. Install virtualenv with `pip install virtualenv`.

## Setting up your workspace

1. Clone the repository with `git clone git@github.com:Shilengae/shilengae-v2-backend.git`.
2. In your repo directory create a new virtualenv with `virtualenv -p python venv`.
3. Activate your new virtualenv with `source venv/bin/activate` (on Mac, Linux) or `source venv/Scripts/activate` (Windows via Git Bash). This should show the `(venv)` prefix on your command line prompt. You can exit the virtualenv with `deactivate`.
4. With `(venv)` activated, install Django and other requirements with `pip install -U -r requirements.txt`.

## Setting up your database

Install PostgreSQL from PostgreSQL Apt Repository

    a) Add PostgreSQL Repository

Import the GPG repository key with the commands:
`sudo apt-get install wget ca-certificates`

`wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -`

Then, add the PostgreSQL repository by typing:
`` sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list' ``

    b) Update the Package List.
    ```sudo apt-get update```

    c)  Install PostgreSQL:
    `sudo apt-get install postgresql postgresql-contrib`

## Create Database

a) Enter an interactive Postgres session by typing:
`sudo -u postgres psql`

    b) ```CREATE DATABASE shilengae;```

    c) Create User for Database: ```CREATE USER shilengae_dev_user WITH PASSWORD 'dev_password';```

    d) We set the default encoding to UTF-8, which is expected by Django:
    ```ALTER ROLE shilengae_dev_user SET client_encoding TO ‘utf8’;```

    e) Set a default transaction isolation scheme to “read commits”:
    ```ALTER ROLE shilengae_dev_user SET default_transaction_isolation TO 'read committed';```

    f) Finally, we set the time zone. By default, our Django project will be set to use UTC:
    ```ALTER ROLE shilengae_dev_user SET timezone TO 'UTC';```

    g) Give our database user access rights to the database that we created:
    ```GRANT ALL PRIVILEGES ON DATABASE shilengae TO shilengae_dev_user;```

    h) Give our shilengae_dev_user access to create test databases
    ```ALTER USER shilengae_dev_user CREATEDB;```

    i) Exit the SQL prompt to return to the postgres user shell session:
    ```\q```

(Optional but Recommended) Install pgAdmin, which is a GUI database management tool for PostgreSQL using this [link](https://www.pgadmin.org/download/pgadmin-4-apt/).

## Development workflow

The 'master' branch always contains the live version of the server. NEVER develop directly on the master branch. When you want to make a change, create a new branch while on 'master' with `git branch new-branch-name` and `git checkout new-branch-name`. After you create your commit locally, run `git push origin new-branch-name` to push your changes to bitbucket. Then go on bitbucket and under "Pull requests" click "create a pull request" and select your branch. Once your changes have been reviewed and approved, they will be merged in to 'master'.
