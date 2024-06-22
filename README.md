# memewebsite
On-premise meme website.
### Backend:
- Flask
- Postgresql
- AWS S3

### Setup database
```
CREATE DATABASE MEME WITH OWNER myuser;
CREATE TABLE USERS (
    UserName VARCHAR(25) NOT NULL,
    Password VARCHAR(32) NOT NULL,
    Email VARCHAR(50),
    EmailVerified BOOLEAN NOT NULL,
	Admin BOOLEAN,
    PRIMARY KEY (UserName)
);

CREATE TABLE POSTS (
    PostID SERIAL,
    Title VARCHAR(50) NOT NULL,
    Url VARCHAR(255) NOT NULL,
    Published INT NOT NULL,
    UserName VARCHAR(25) NOT NULL,
    Approver VARCHAR(25),
    FOREIGN KEY (UserName) REFERENCES users(UserName),
    FOREIGN KEY (Approver) REFERENCES users(UserName),
	PRIMARY KEY (PostID)
);

CREATE TABLE VOTES (
	PostID INT NOT NULL,
	UserName VARCHAR(25) NOT NULL,
	Vote SMALLINT NOT NULL CHECK (Vote IN (-1, 1)),
	FOREIGN KEY (PostID) REFERENCES posts(PostID),
	FOREIGN KEY (UserName) REFERENCES users(UserName)
);
```