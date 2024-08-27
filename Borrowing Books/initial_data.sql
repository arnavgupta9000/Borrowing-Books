/* Relational Schema
members (email, passwd, name, byear, faculty)
books (book_id, title, author, pyear)
borrowings (bid, member, book_id, start_date, end_date)
penalties (pid, bid, amount, paid_amount)
reviews (rid, book_id, member, rating, rtext, rdate)
*/

-- populating members relation
INSERT INTO members
VALUES
-- email, passwd, name, byear, faculty
("skhrange@ualberta.ca", "p", "Suryansh Khranger", 2004, "Science"),
("arnav6@ualberta.ca", "p", "Arnav Gupta", 2004, "Science"),
("adhal@ualberta.ca", "p", "Aarman Dhal", 2004, "Science"),
("balqasem@ualberta.ca", "p", "Bader Alqasem", 2004, "Science");

-- populating books relation
INSERT INTO books
VALUES
-- book_id, title, author, pyear
(1, "book1", "author1", 2000),
(2, "book2", "author2", 2001),
(3, "book3", "author2", 2002),
(4, "book4", "author2", 2003),
(5, "book5", "author2", 2005),
(6, "book6", "author3", 2003),
(7, "Ring of Fire", "author3", 2007);





-- populating borrowings relation
INSERT INTO borrowings
VALUES
-- bid, member, book_id, start_date, end_date
-- current (unreturned) borrowings; these arent yet overdue
(1, "adhal@ualberta.ca", 3, "2024-03-03", NULL),
(2, "arnav6@ualberta.ca", 2, "2024-03-03", NULL),
(3, "balqasem@ualberta.ca", 4, "2024-03-03", NULL),
(4, "skhrange@ualberta.ca", 1, "2024-03-03", NULL),
-- previous (returned) borrowings
(5, "adhal@ualberta.ca", 3, "2024-01-01", "2024-01-01"),
(6, "arnav6@ualberta.ca", 2, "2024-01-02", "2024-01-02"),
(7, "balqasem@ualberta.ca", 4, "2024-01-03", "2024-01-03"),
(8, "skhrange@ualberta.ca", 1, "2024-01-04", "2024-01-04"),
-- overdue borrowings (current borrowings, not returned by deadline); deadline:= 20 days after start_date
(9, "adhal@ualberta.ca", 3, "2024-01-01", NULL),
(10, "arnav6@ualberta.ca", 2, "2024-01-02", NULL),
(11, "balqasem@ualberta.ca", 4, "2024-01-03", NULL),
(12, "skhrange@ualberta.ca", 1, "2024-01-04", NULL);

-- populating penalties relation
INSERT INTO penalties
VALUES
-- pid, bid, amount, paid_amount
(1, 1, 10, 0),
(2, 3, 10, 0),
(3, 1, 20, 30),
(4, 3, 20, 30);
-- note: even though they pay enough to cover prev penalties, the instruction specs say that:
-- "The system should show a list of unpaid penalties (any penalty that is not paid in full) of the user. The user should be able to select a penalty and pay it partially or in full.""
-- so its a individual penalty-by-penalty basis (as far as I can tell)...
-- thats what it was like in the prev assignment, so im going with that
-- its kind of ambigious tho...

-- populating reviews relation
INSERT INTO reviews
VALUES
-- rid, book_id, member, rating, rtext, rdate
(1, 2, "arnav6@ualberta.ca", 7, '', "2025-01-01"),
(2, 4, "skhrange@ualberta.ca", 3, '', "2025-01-01"),
(3, 2, "arnav6@ualberta.ca", 9, '', "2025-01-01"),
(4, 4, "skhrange@ualberta.ca", 1, '', "2025-01-01");
