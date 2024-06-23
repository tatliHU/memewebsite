# memewebsite
Multi-cloud meme website.

## You will need
- AWS account with an S3 bucket
- Your own domain

### Planned features
- Email verification
- Domain
- Automatic certificate creation and renewal with Let's encrypt

## Backend stack:
- Flask
- Postgresql-16
- AWS S3
- Hetzner Cloud Server
I use Hetzner hosting because it is extremly cheap. You should be able to use the same cloud-init file with other cloud providers.

## Remote setup with Terraform
- Create a Hetzner account and a project with a read-write API key
- Replace token in terraform/terraform.tfvars
- Open a shell in the terraform folder and execute
```
terraform init
terraform apply
```

## Local setup

### Setup database
```
CREATE DATABASE MEME WITH OWNER myuser;
CREATE TABLE USERS (
    UserName VARCHAR(25) NOT NULL,
    Password VARCHAR(32) NOT NULL,
    Email VARCHAR(50) NOT NULL,
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

CREATE TABLE EMAILS (
    EmailUUID VARCHAR(36) NOT NULL,
	UserName VARCHAR(25) NOT NULL,
	FOREIGN KEY (UserName) REFERENCES users(UserName),
    PRIMARY KEY (EmailUUID)
);
```