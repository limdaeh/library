PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS mainmenu (
id integer PRIMARY KEY AUTOINCREMENT, 
title text NOT NULL, 
url text NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
id integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
email text NOT NULL,
psw text NOT NULL,
avatar BLOB DEFAULT NONE,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
bookid integer PRIMARY KEY AUTOINCREMENT,
name text NOT NULL,
author text NOT NULL,
genre text NOT NULL,
preview BLOB DEFAULT NONE,
isbn integer UNIQUE NOT NULL,
pages integer NOT NULL,
phouse text NOT NULL,
year integer NOT NULL,
edition integer NOT NULL,
availibility integer NOT NULL
);

CREATE TABLE IF NOT EXISTS usersandbooks (
    id integer,
    bookid integer,
    days integer,
    FOREIGN KEY (id) REFERENCES users(id),
    FOREIGN KEY (bookid) REFERENCES books(bookid)
);

CREATE TABLE IF NOT EXISTS groups (
    groupid integer PRIMARY KEY AUTOINCREMENT,
    groupname text NOT NULL
);

CREATE TABLE IF NOT EXISTS usersliked (
    id integer,
    bookid integer,
    groupid integer,
    FOREIGN KEY (id) REFERENCES users(id),
    FOREIGN KEY (bookid) REFERENCES books(bookid),
    FOREIGN KEY (groupid) REFERENCES groups(groupid)
);

