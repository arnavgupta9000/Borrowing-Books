"""
TITLE: MINI-PROJECT 1
AUTHORS: SURYANSH KHRANGER, Arnav Gupta
DATE CREATED: 2024-03-02
REFERENCES: https://www.geeksforgeeks.org/python-store-function-as-dictionary-value/, https://www.w3schools.com/sql/func_sqlserver_getdate.asp, https://www.w3schools.com/python/ref_func_next.asp
"""

# IMPORTS
## LIBRARIES
import sqlite3
import getpass
import sys   
## MODULES

# SUBPROGRAMS
## CLASSES
## FUNCTIONS
### login
def login_screen() -> int:
    '''
    presents users with option to either login as an existing user, or make a new account
    '''
    print('''
        1. Login as an existing user
        2. Create an account
    ''')
     
    choice = input("> ")
    while True:
        if choice == '1' or choice == '2':
            return int(choice)
        else:
            print("Please make a valid selection (1 or 2)")
            choice = input("> ")


def try_logging_in(db_file_name: str, email: str, password: str) -> bool:      # correct functionality + SQL injection protection
    # run a querry to locate exactly the combo of email and passowrd in the members relation
    query = '''
        SELECT *
        FROM members m
        WHERE LOWER(email) = LOWER(?)   -- Case-insensitive comparison
        AND passwd = ?;
    '''

    # Connect to the SQLite database
    connection = sqlite3.connect(db_file_name)
    cursor = connection.cursor()

    # there SHOULDNT be duplicate email, passwd combos, so im not gonna check for dupes; just use fetchone()
    res = cursor.execute(query, (email, password)).fetchone()            # run the query, fetch 1st (hopefully ONLY) result

    # NOTE: the .execute(query, (params,)) prevents SQL injections attacks by using parameterized querries
    # it would be vulnerable to SQL injection attacks <-> I had used
        # query = 'SELECT * ...'.format(params,)
        # cursor.execute(query)
    
    # Close the connection
    connection.commit();connection.close()


    # Check if a row was found (login successful)
    return res != None


def register_new_user(db_file_name) -> {bool, str}:
    """
    adds a new user into the db.
    if successful returns the email of the newly registered user.
    if not, returns itself until successful.
    """
    new_username = input("username (email) > ") ## dropped the .lower() as it should be case sensitive https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=2472003
    if len (new_username) == 0:
        return (False, 'email cannot be empty') 
    
    # Check if the username already exists in the database
    check_query = '''
        SELECT COUNT(*)
        FROM members
        WHERE LOWER(email) = LOWER(?);  -- Case-insensitive comparison
    '''
    connection = sqlite3.connect(db_file_name)
    cursor = connection.cursor()

    # Execute the query to count the number of rows with the given email
    cursor.execute(check_query, (new_username,))
    count = cursor.fetchone()[0]

    if count > 0:                                                           # username (email) already exists
        print("Email already in use. If it's you log in!")
        main(db_file_name)


    new_password = input("password > ")
    if len(new_password) == 0:
        return (False, 'password cannot be empty')

    new_name = input("full name > ").capitalize()
     
    new_birth_year = input("year of birth > ")
    new_faculty = input("faculty > ").capitalize()


    # add tuple into members relation <-> there isnt already a row with that exact username (email)
    insertion_query = '''
        INSERT INTO members
        VALUES (?, ?, ?, ?, ?);
    '''

    # Execute the query with user-inputted values
    cursor.execute(insertion_query, (new_username, new_password, new_name, new_birth_year, new_faculty))

    # Commit the transaction, close the connection
    connection.commit();connection.close()

    print(f"successfully added user {new_username}")

    return (True, new_username)

### functionality
def select_option() -> int:                                 # works
    print('''
        1. Profile
        2. Return a Book
        3. Search Books
        4. Penalty Payment
        5. Exit
    ''')
   
    user_input = input("> ")
    while True:
        if user_input.isnumeric() and int(user_input) in {1,2,3,4,5}:
            return int(user_input)
        else:
            print(f"Invalid input: {user_input}. Please make a valid input.")
            user_input = input("> ")

#### view profile
def view_profile(db_file_name: str, email: str) -> None:                       

    """
    displays user's: 
        - personal information (name, email, birth year)
        - the number of the books they have borrowed and returned (shown as previous borrowings)
        - the current borrowings which is 
            - the number of their unreturned borrowings, and
            - overdue borrowings
                - which is the number of their current borrowings that are not returned within the deadline. The return deadline is 20 days after the borrowing date.
        - the penalty information
            - the number of unpaid penalties
                - (any penalty that is not paid in full),
            - the user's total debt amount on unpaid penalties.
    parameters:
        - email: str. the email of the user we are ghetting this info for
    """
    # access db
    connection = sqlite3.connect(db_file_name)
    cursor = connection.cursor()

    # fetch info
    query = '''
        SELECT
            m.name,
            m.email,
            m.byear,
            COUNT(
                DISTINCT CASE WHEN br.end_date IS NOT NULL
                THEN br.bid 
            END) AS previous_borrowings,    
            COUNT(
                DISTINCT CASE WHEN br.end_date IS NULL 
                THEN br.bid
            END) AS current_borrowings,
            COUNT(
                DISTINCT CASE WHEN br.end_date IS NULL
                AND DATE(br.start_date, '+20 days') < DATE('now')
                THEN br.bid
            END) AS overdue_borrowings,
            COUNT(
                DISTINCT CASE WHEN p.paid_amount < p.amount
                THEN p.pid
            END) AS unpaid_penalties,
            SUM(
                CASE WHEN p.paid_amount < p.amount
                THEN p.amount - p.paid_amount
                ELSE 0
            END) AS total_debt
        FROM members m
        LEFT JOIN borrowings br ON m.email = br.member
        LEFT JOIN books b ON br.book_id = b.book_id
        LEFT JOIN penalties p ON br.bid = p.bid
        WHERE LOWER(m.email) = LOWER(?)                 -- Case-insensitive comparison
        GROUP BY m.name, m.email, m.byear;
    '''
    result = cursor.execute(query, (email,)).fetchone()
    # Commit and close the connection
    connection.commit(); connection.close()

    # a bit nicer terminal based display
    print(f'''
    Personal Information
        Name: {result[0]}
        Email: {result[1]}
        Birth Year: {result[2]}

    Previous Borrowings: {result[3]}
    Current Borrowings: {result[4]}
    Overdue Borrowings: {result[5]}
    Unpaid Penalties: {result[6]}
    Total Debt Owing: {result[7]}
    ''')


### return a book
def display_current_borrowings(db_file_name: str, email: str) -> None:
    """
    displays the given user's current borrowings
    return: None
    """
    # access db
    connection = sqlite3.connect(db_file_name)
    cursor = connection.cursor()

    # get current borrowings
    query = '''
        SELECT 
            br.bid,
            b.title,
            br.start_date,
            DATE(br.start_date, '+20 days') AS return_deadline
        FROM
            books b, borrowings br
        WHERE LOWER(br.member) = LOWER(?)               -- Case-insensitive comparison
        AND br.book_id = b.book_id
        AND br.end_date IS NULL;
    '''

    result = cursor.execute(query, (email,)).fetchall()
    
    # Commit and close the connection
    connection.commit(); connection.close()
    
    
    # nicer display
    def display_borrowings(list_of_borrowings_tuples: list) -> None:                # local function
        """
        displays the borrowings nicely
        returns None
        param:
            -list_of_borrowings_tuples: its exactly as it sounds...
        """
        print("Borrowings:")
        print("-----------")
        for tupple in list_of_borrowings_tuples:
            print("Borrowing ID:", tupple[0])
            print("Book Title:", tupple[1])
            print("Start Date:", tupple[2])
            print("Return Deadline:", tupple[3])
            print("")

    display_borrowings(result)
    

def return_book(db_file_name: str, email: str) -> None:                      
    """
    Features:
        - First the system should display the user's current borrowings, as a list of:
            - the borrowing id
            - book title
            - borrowing date
            - return deadline for each unreturned borrowing (including overdue ones).
                - The return deadline is 20 days after the borrowing date.
                
        - User can pick a borrowing to return, and the system should record today’s date as the returning date.
        - The system must apply a penalty of $1 per every delayed day after the deadline.
            - For example, if a book is returned after 25 days, the user will get a penalty of $5 for this borrowing.
        - User should be given an optional choice to write a review for the book by providing a review text and a rating (a number between 1 and 5 inclusive);
            - the other fields of a review record should be appropriately filled by the application. In particular, a unique review id is recorded, the review date is set to the current date and time, and the user should be recorded as the reviewer.
    parameters:
        - email: value corresponding to the borrowings.member field from the db
    """

    # display current borrowings

    # connect to db
    connection = sqlite3.connect(db_file_name)
    cursor = connection.cursor()

    # CASE 1: No current borrowings
    # check if the user has any current borrowings
    num_current_borrowings_query = '''
        SELECT COUNT(*)
        FROM borrowings
        WHERE member = ? AND end_date IS NULL;
    '''

    query_for_res = '''
    select bid
    from borrowings
    where member = ? and end_date is NULL
    '''
    
    num_current_borrowings = cursor.execute(num_current_borrowings_query, (email,)).fetchone()[0]

    #fixed the returning of other users  
    borrows = list(cursor.execute(query_for_res, (email,)).fetchall())
    hash_map = {}
    for i in range(len(borrows)):
        for j in range(len(borrows[i])):
            if borrows[i][j] not in hash_map:
                hash_map[borrows[i][j]] = True
    

    if num_current_borrowings == 0:                         # exit the function if there are no borrowings
        print("You have no current borrowings.")
        return
    display_current_borrowings(db_file_name, email)

    # CASE 2: Has current borrowings
    # returning a book
    return_bid = input("Enter the Borrowing ID of the book you wish to return > ")      # select bid
    while not return_bid.isnumeric() or int(return_bid) not in hash_map:
        return_bid = input("Enter the Borrowing ID of the book you wish to return > ")
    return_bid = int(return_bid)


    return_query = '''
        -- update borrowings.end_date for this borrowing
        UPDATE borrowings
        SET end_date = CURRENT_DATE
        WHERE bid = ?;
    '''

    penalty_query = '''
        -- insertion stmt
        INSERT INTO penalties (bid, amount, paid_amount)
        -- values stmt
        -- NOTE: I used ? here instead of br.bid because it prevents SQL injection attacks, whatever that means..., and also because it ensures that the calculation takes into account the specific borrowing ID for which the book is being returned, rather than relying on the borrowing ID of the current row in the borrowings table. (whatever that means)
        SELECT ?, (JULIANDAY(CURRENT_DATE) - JULIANDAY(br.start_date) - 20) * 1, 0        -- this is #days past deadline * penalty_rate/day
        FROM borrowings br
        WHERE br.bid = ?                                                                -- this penalty corresponds to this particular borrowing
        AND JULIANDAY(CURRENT_DATE) > (JULIANDAY(br.start_date) + 20)                   -- check if penalty needs to be applied
        AND NOT EXISTS (                                                                -- not sure I need this, but its to prevent duplicate entries of the exact same penalty
            SELECT 1
            FROM penalties p
            WHERE p.bid = br.bid
        );
    '''

    # return the book
    cursor.execute(return_query, (return_bid,))


    # make entry into penalties if needed
    cursor.execute(penalty_query, (return_bid,return_bid,))

    # ask the user if they would like to add a review
    review_input = input("Would you like to make an review? (y/n) > ").lower()
    while review_input not in ['y','n']:
        review_input = input("Please type 'y' or 'n'. Would you like to make an review? (y/n) > ").lower()
    
    if review_input == 'y':
        # find the unique rid, join on book_id, member is email, rating is input, rtext is input, rdate is CURRENT_DATE
        while True:
            try:
                stars = int(input("Enter a rating between 1-5\n"))
                if stars >= 1 and stars <=5:
                    break
                else:
                    print("Please enter a number between 1-5")
            except(TypeError, ValueError) as error:
                print("Thats not a valid number. Please enter a number between 1-5\n")
        text = str(input("please input what you thought about the text \n"))
        # getting the book_id of the borrowings we are writing a review for
        get_book_id_query = '''
            SELECT book_id
            FROM borrowings
            WHERE bid = ?;
        '''
        # execute the query
        book_id = cursor.execute(get_book_id_query, (return_bid,)).fetchone()[0]

        review_query = '''
            INSERT INTO reviews (book_id, member, rating, rtext, rdate)
            VALUES (?,?,?,?, CURRENT_DATE);
        '''
        
        cursor.execute(review_query, (book_id, email, stars, text, ))
            
    # Commit and close the connection
    connection.commit(); connection.close()


### search for a book
def search_book(db_file_name: str, keyword: str) -> bool:
    """
    functionality:
        - The user should be able to enter a keyword and the system should retrieve all books in which the title or author contain the keyword
        - Sorting. The result would be sorted as follows:
            - first, all books with a title matching the keyword would be listed and should be sorted in an ascending order of their title.
            - this would be followed by the list of books with only their author matching the keyword and this result would be sorted in an ascending order of the author’s name.
        - For each book, the system must display:
            1. book id
            2. title
            3. author
            4. publish year
            5. average rating
            6. whether the book is available or on borrow.
                6.1 If a book is available, the user should be given an option to borrow the book
        
        - Borrow a Book:
            - Users can select a book id to borrow 
                - if the book is already borrowed, the system should prevent the borrowing.
            - System automatically assigns a unique number to bid and sets the today’s date as start date.
    """

    limit_books_per_page = 5
    listing_offset = 0
    ##make a helper function to allow us to see 5 pages at a time
    
    more_books = True
    while more_books:
        more_books = search_book_helper(db_file_name, keyword, limit_books_per_page, listing_offset)
        listing_offset += 5 # keep displaying the first 5 results, then the next 5 then the next 5 etc
        if more_books:
            choice = input('See next 5 books that match result? Type "n". Want to borrow a book? Type "b". Want to Exit? Type "e" \n').lower()
            while choice != 'n' and choice !='b' and choice != 'e':
                choice = input('See next 5 books that match result? Type "n". Want to borrow a book? Type "b". Want to Exit? Type "e" \n').lower()

            if choice == 'b':
                return True
            if choice == 'e':
                return False
    return False # they went through all the pages

def search_book_helper(db_file_name, keyword, limit, offset, rec = False) -> bool: # query is the query, limit is the amonut of books per page, and offset is the current offset we're at

    query = f'''
        SELECT b.book_id, b.title, b.author, b.pyear, AVG(rating), 
        CASE 
            WHEN EXISTS (SELECT 1 FROM borrowings WHERE book_id = b.book_id AND end_date IS NULL) THEN 'Borrowed' 
            ELSE 'Available' 
        END AS availability
        FROM books b
        LEFT JOIN borrowings ON borrowings.book_id = b.book_id
        LEFT JOIN reviews ON reviews.book_id = b.book_id
        WHERE title LIKE '%{keyword}%'
        OR author LIKE '%{keyword}%'
        GROUP BY b.book_id
        ORDER BY
            title LIKE '%{keyword}%' DESC,
            author LIKE '%{keyword}%' DESC,
            title ASC
        LIMIT {limit}
        OFFSET {offset}
    '''

    connection = sqlite3.connect(db_file_name)
    cursor = connection.cursor()
    res = cursor.execute(query)
    # calculate the length        
    if rec:
        if len(res.fetchall()) == 0:
            # dont display a next user input
            return False
        return True
            
    # displaying results
    for book in res:
        print(book)
    # rerun the query to see if there are MORE BOOKS AVALIABLE
    # NOTICE USING THE PARAMATER 'rec' IT WILL ONLY RUN IT HERE AND NOT CHANGE ANYTHING
    # the max depth stack call is 1 always. this will just see if theres more books to show a next page or not
    return search_book_helper(db_file_name, keyword, limit, offset + 5, True)


def borrow_a_book(db_file_name: str, email: str, catch: bool, keyword:str) -> None:
    """
    Users can select a book id to borrow and if the book is already borrowed, the system should prevent the borrowing. System automatically assigns a unique number to bid and sets the today’s date as start date.

    parameters
        - email: the username/email of the user who is trying to borrow a book
    """
    if not catch:
        user_borrow_input = input("Do you wish to borrow a book? (y/n) > ").lower()
        while user_borrow_input not in ['y','n']:    # validate input
            user_borrow_input = input("please make a valid input (y/n) > ")
 
    if catch or user_borrow_input.lower() == 'y':                    # wants to borrow
        query_availible_books = f'''
        SELECT b.book_id, b.title, b.author, b.pyear, AVG(rating), 
        CASE 
            WHEN EXISTS (SELECT 1 FROM borrowings WHERE book_id = b.book_id AND end_date IS NULL) THEN 'Borrowed' 
            ELSE 'Available' 
        END AS availability
        FROM books b
        LEFT JOIN borrowings ON borrowings.book_id = b.book_id
        LEFT JOIN reviews ON reviews.book_id = b.book_id
        WHERE title LIKE '%{keyword}%'
        OR author LIKE '%{keyword}%'
        GROUP BY b.book_id
        HAVING availability = 'Available'
        ORDER BY
            title LIKE '%{keyword}%' DESC,
            author LIKE '%{keyword}%' DESC,
            title ASC
    '''
        connection = sqlite3.connect(db_file_name)
        cursor = connection.cursor()
        cursor.execute(query_availible_books)
        availible_books = cursor.fetchall()

        #make a hash map to see if they picked a book that can be borrowed
        borrow_available = {}
        for i in range(len(availible_books)):
            if availible_books[i] not in borrow_available:
                borrow_available[availible_books[i][0]] = True

        if len(availible_books) == 0:
            print("No books matching those keyword(s) are avaliable")
            return

        print("Availible Books:")
        for book in availible_books:
            print(f"book_id: {book[0]}") # book[0] drops the tuple

        #add a unique bid - get the max bid and add 1, this will ENSURE a unique bid

        unique_bid = '''
            select MAX(bid) from borrowings b;
        '''

        bid = cursor.execute(unique_bid).fetchone()[0] + 1 # add one to make sure its unique

        selected_book_id = input("Please enter the book id of the book you want to borrow: ")
        # validate input
        while not selected_book_id.isnumeric() or int(selected_book_id) not in borrow_available:
            selected_book_id = input("Please a valid numeric book id: ")
        selected_book_id = int(selected_book_id)
        
        # borrow the selected book
                
        borrow_query = f'''
            INSERT INTO borrowings (bid, member, book_id, start_date, end_date)
            VALUES (?, ?, ?, CURRENT_DATE, NULL)
        ;'''
        cursor.execute(borrow_query, (bid, email, selected_book_id,))
        # Commit and close the connection
        connection.commit();connection.close()

    else:                                                   # doesnt want to borrow
        return

### pay a penalty
def pay_penalty(db_file_name: str, email: str) -> None:
    """
    The system should show a list of unpaid penalties (any penalty that is not paid in full) of the user. The user should be able to select a penalty and pay it partially or in full.
    
    param:
        - email: the username/email of the user
    """
    # get unpaid penalties
    get_pending_penalties_query = '''
        SELECT p.pid, p.bid, p.amount, (p.amount - p.paid_amount) AS amount_owing
        FROM penalties p
        JOIN borrowings br ON p.bid = br.bid
        WHERE br.member = ?
    ;'''

    connection = sqlite3.connect(db_file_name)
    cursor = connection.cursor()

    result = cursor.execute(get_pending_penalties_query, (email,)).fetchall()

    #checking to see if they have any penalties or not
    if not result:
        print('You have no penalties')
        return 
    # this for if we paid the penalty in 'option 4' fully, it doesnt actually drop the penalty so we need to see if there are any unpaid penalties
    no_pen = True
    for i in range(len(result)):
        if result[i][3] > 0:
            no_pen = False
    if no_pen:
        print('You have no penalties')
        return 
    
    for tup in result:
        ## checking to see if they have to pay less than 0 ie dont display it
        if tup[3] > 0:
            print("pid: ", tup[0]); print("bid: ", tup[1]); print("peanlty amount: ", tup[2]); print("amount owing: ", tup[3]); print("")
    # making payment
    selected_pid = input("Select the pid of the penalty you want to pay > ")
    valid = False
    
    # checking to see if its a valid pid
    while not valid:
        try:
            for i in range(len(result)):
                if int(result[i][0]) == int(selected_pid) and result[i][3] > 0: # result[i][3] > 0 - make sure we dont try to pay a penatly thats already paid 
                    valid = True
            if not valid:
                print("Thats not a valid pid")
        except (TypeError, ValueError) as error:
            print("thats not a number try again")
        if not valid:
            selected_pid = input("Select the pid of the penalty you want to pay > ")
    
    paying_amount = input("Enter amount you want to pay > ")

    # paying too much is fine by the forum post of: https://eclass.srv.ualberta.ca/mod/forum/discuss.php?d=2468875

    while not paying_amount.isnumeric() or int(paying_amount) <= 0:                            # validating input is numeric
        paying_amount = input("Please enter a valid numeric amount (greater than 0) you want to pay > ")
    paying_amount = int(paying_amount)

    make_payment_query = '''
        UPDATE penalties
        SET paid_amount = paid_amount + ?
        WHERE pid = ?
    ;'''
    
    cursor.execute(make_payment_query, (paying_amount, selected_pid))

    connection.commit(); connection.close()

def display_main_screen(dbfile_name:str, user_email:str) -> None:
    print("Login successful. Welcome!")
    while True:                                             # subsequent operations
        function_input = select_option()
        if function_input == 1:                             # Profile
            view_profile(dbfile_name, user_email)
        elif function_input == 2:                           # Return a Book
            return_book(dbfile_name, user_email)
        elif function_input == 3:                           # Search Books
            keyword = input("Enter keyword to search: ")
            catch = search_book(dbfile_name, keyword)
            borrow_a_book(dbfile_name, user_email, catch, keyword)
        elif function_input == 4:                           # Penalty Payment
            pay_penalty(dbfile_name, user_email)
        elif function_input == 5:                           # Exit
            print("Closing Session... goodbye.")
            quit()

### MAIN FUNCTION
def main(dbfile_name):              
    # actual program functionality
    login_input = login_screen()
    while True:
        if login_input == 1:                                            # exisitng user logining in
            # ask for email and password
            user_email = input("email > ")
            # user_password = input("password > ")                      # does not hide password at typing time
            user_password = getpass.getpass("password > ")              # hides password while typing

            success = try_logging_in(dbfile_name, user_email, user_password)         # attempt login
            if success:                                                 # successful login
               display_main_screen(dbfile_name, user_email)
            else:                                                       
                print("Invalid login details... Try again.")
                main(dbfile_name)

        elif login_input == 2:                                          # new user, creating an account
            valid, new_user_email = register_new_user(dbfile_name)
            if not valid: # in the case that some fields arent filled out
                print(new_user_email) # print the error
                main(dbfile_name) # make the user re select what they wanna do
            display_main_screen(dbfile_name, new_user_email)
        else:                                                           # invalid selection, somehow uncaught in login function
            print("Please make a valid selection...")
            main(dbfile_name)
        

# MAIN PROGRAM CODE
if __name__ == "__main__":
    # instructions:
        # At demo time, you will be given a database file name that has our test data (e.g., prj-test.db)
        # and you MUST be passing the file name to your application as a command line argument.
    if len(sys.argv) != 2:
        print("missing command line argument: database file name")
        print("Usage: python script_name.py file_name")
        sys.exit(1)
    file_name = sys.argv[1]
    main(file_name)