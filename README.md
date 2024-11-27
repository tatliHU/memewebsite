# memewebsite

Multi-cloud meme website designed to opearate on ultra-low infra budget.

## You will need

- AWS account with an S3 bucket
- Your own domain

## Backend stack

- Python
- Flask
- Gunicorn
- HAproxy
- Postgresql-16
- AWS S3
- Hetzner Cloud Server

    > I use Hetzner hosting because it is extremly cheap. You should be able to use the same cloud-init file with other cloud providers.

- Amazon SES
For sending registration verification emails.

### Configurable options

These are all configured as env vars:

- `SESSION_KEY`\
  Security feature for encoding cookies
- `AWS_REGION`\
  AWS region of your S3 bucket
- `S3_BUCKET`\
  AWS S3 bucket name for storing the images
- `POSTGRES_HOST`\
  Your database server URL
- `POSTGRES_PORT`\
  Your database server port
- `POSTGRES_DB`\
  Database to use
- `POSTGRES_USER`\
  User to connect to the database server
- `POSTGRES_PASS`\
  Password to connect to your database server
- `DOMAIN`\
  Your domain configured in your Amazon SES for registration verification emails
- `WEBSITE_URL`\
  URL (and optionally port) your website listens on. Example: <https://mysite.com:5000>
- AWS access related env vars

## Remote setup with Terraform

- Create a Hetzner account and a project
- Create AWS account
- Replace tokens in terraform/terraform.tfvars
- Open a shell in the terraform folder and execute
- (Optional for email verification) Configure AWS SES\
Create identity and verify ownership of your domain and email. Request to be moved outisde the sandbox so you can send emails to any user.

```bash
terraform init
terraform apply
```

## Local setup

### Configure environment variables

You can use the presets for testing.

### Start webserver

```bash
flask --app main run --debug
```

### Setup a postgres database and execute SQL

You can use the following to bring up a postgres database in a docker container.

```bash
docker compose -f compose.dev.yaml up -d
```

Then you can create the database and tables with the following command.
> Replace the username and database name with your own if needed.

```bash
psql -h localhost -U atka -d meme -f docs/db_init.sql
```

Instead can use the following SQL to setup your database.

```sql
CREATE USER atka WITH PASSWORD 'atka';
CREATE DATABASE meme WITH OWNER atka;
\c meme;
CREATE EXTENSION tsm_system_rows;
CREATE TABLE users (
    username VARCHAR(25) NOT NULL,
    password TEXT NOT NULL,
    email VARCHAR(50) NOT NULL,
    admin BOOLEAN DEFAULT false,
    PRIMARY KEY (username)
);

CREATE TABLE posts (
    post_id SERIAL,
    title VARCHAR(50) NOT NULL,
    url VARCHAR(255) NOT NULL,
    published INT NOT NULL,
    username VARCHAR(25) NOT NULL,
    approver VARCHAR(25),
    approved BOOLEAN,
    tag_all BOOLEAN DEFAULT false,
    tag_emk BOOLEAN DEFAULT false,
    tag_gpk BOOLEAN DEFAULT false,
    tag_epk BOOLEAN DEFAULT false,
    tag_vbk BOOLEAN DEFAULT false,
    tag_vik BOOLEAN DEFAULT false,
    tag_kjk BOOLEAN DEFAULT false,
    tag_ttk BOOLEAN DEFAULT false,
    tag_gtk BOOLEAN DEFAULT false,
    FOREIGN KEY (username) REFERENCES users(username),
    FOREIGN KEY (approver) REFERENCES users(username),
 PRIMARY KEY (post_id)
);

CREATE TABLE votes (
 post_id INT NOT NULL,
 username VARCHAR(25) NOT NULL,
 vote SMALLINT NOT NULL CHECK (vote IN (-1, 1)),
 FOREIGN KEY (post_id) REFERENCES posts(post_id),
 FOREIGN KEY (username) REFERENCES users(username)
);

CREATE TABLE pending_registrations (
    email VARCHAR(40) NOT NULL,
    uuid VARCHAR(36) NOT NULL,
 username VARCHAR(25) NOT NULL,
    password TEXT NOT NULL,
    created INT NOT NULL,
    PRIMARY KEY (email)
);

CREATE TABLE pending_passwords (
    email VARCHAR(40) NOT NULL,
    uuid VARCHAR(36) NOT NULL,
    username VARCHAR(25) NOT NULL,
    created INT NOT NULL,
    PRIMARY KEY (email)
);

GRANT ALL PRIVILEGES ON TABLE users TO atka;
GRANT ALL PRIVILEGES ON TABLE posts TO atka;
GRANT ALL PRIVILEGES ON TABLE votes TO atka;
GRANT ALL PRIVILEGES ON TABLE pending_registrations TO atka;
GRANT ALL PRIVILEGES ON TABLE pending_passwords TO atka;
GRANT USAGE, SELECT, UPDATE ON SEQUENCE posts_post_id_seq TO atka;
```
