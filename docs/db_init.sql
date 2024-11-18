DO
$do$
BEGIN
    -- CREATE USER atka IF NOT EXISTS WITH PASSWORD 'atka';
   IF NOT EXISTS ( SELECT FROM pg_roles  
                   WHERE  rolname = 'atka') THEN
      CREATE USER atka WITH PASSWORD 'atka';
   END IF;
    -- CREATE DATABASE meme IF NOT EXISTS WITH OWNER atka;
   IF NOT EXISTS ( SELECT FROM pg_database WHERE datname = 'meme') THEN
      CREATE DATABASE meme WITH OWNER = atka;
   END IF;
END
$do$;

\c meme;
CREATE EXTENSION IF NOT EXISTS tsm_system_rows;
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(25) NOT NULL,
    password TEXT NOT NULL,
    email VARCHAR(50) NOT NULL,
    admin BOOLEAN DEFAULT false,
    PRIMARY KEY (username)
);

CREATE TABLE IF NOT EXISTS posts (
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

CREATE TABLE IF NOT EXISTS votes (
 post_id INT NOT NULL,
 username VARCHAR(25) NOT NULL,
 vote SMALLINT NOT NULL CHECK (vote IN (-1, 1)),
 FOREIGN KEY (post_id) REFERENCES posts(post_id),
 FOREIGN KEY (username) REFERENCES users(username)
);

CREATE TABLE IF NOT EXISTS pending_registrations (
    email VARCHAR(40) NOT NULL,
    uuid VARCHAR(36) NOT NULL,
 username VARCHAR(25) NOT NULL,
    password TEXT NOT NULL,
    created INT NOT NULL,
    PRIMARY KEY (email)
);

CREATE TABLE IF NOT EXISTS pending_passwords (
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