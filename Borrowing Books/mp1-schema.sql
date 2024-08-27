drop table if exists reviews;
drop table if exists penalties;
drop table if exists borrowings;
drop table if exists books;
drop table if exists members;




PRAGMA foreign_keys = ON;

CREATE TABLE members (
    email CHAR(100),
    passwd CHAR(100),
    name CHAR(255) NOT NULL,
    byear INTEGER,
    faculty CHAR(100),
    PRIMARY KEY (email)
);

CREATE TABLE books (
    book_id INTEGER,
    title CHAR(255),
    author CHAR(150),
    pyear INTEGER,
    PRIMARY KEY (book_id)
);

CREATE TABLE borrowings(
    bid INTEGER,
    member CHAR(100) NOT NULL,
    book_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    PRIMARY KEY (bid),
    FOREIGN KEY (member) REFERENCES members(email),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);


CREATE TABLE penalties(
    pid INTEGER,
    bid INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    paid_amount INTEGER,
    PRIMARY KEY (pid),
    FOREIGN KEY (bid) REFERENCES borrowings(bid)
);


CREATE TABLE reviews(
    rid INTEGER,
    book_id INTEGER NOT NULL,
    member CHAR(100) NOT NULL,
    rating INTEGER NOT NULL,
    rtext CHAR(255),
    rdate DATE,
    PRIMARY KEY (rid),
    FOREIGN KEY (member) REFERENCES members(email),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);