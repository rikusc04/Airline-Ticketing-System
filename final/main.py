#Riku Santa Cruz
#Airline Website

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
# import pymysql.cursors
import pymysql
from hashlib import md5
from datetime import *

'''

Make sure to check whether each one is a post or get method:
    
Checking whether the request method is POST or GET is a common practice in web development, especially when handling form submissions. Here's why it's important:

GET Request: This method is typically used for fetching data from the server. When a user initially loads a page or follows a link, the browser sends a GET request
to the server. In your Flask route, when the method is GET, you might want to render the login form for the user to fill out.
POST Request: This method is used when the user submits a form or sends data to the server to be processed. When the user fills out the login form and clicks the
submit button, the browser sends a POST request to the server with the form data. In your Flask route, when the method is POST, you need to process the form 
data submitted by the user.

'''

app = Flask(__name__)

app.secret_key = 'my_secret_key'
# app.config['SECRET_KEY'] = 'my_secret_key'

# Establish connection to MySQL database
db = pymysql.connect(host="localhost", 
                   port = 3306,
                   user="root", 
                   password="", 
                   database="air_ticket_system", 
                   charset="utf8mb4", 
                   cursorclass=pymysql.cursors.DictCursor
)

# cursor = db.cursor()
# @app.before_first_request
# def init_db():
#     db.ping(reconnect=True)



# Function to check whether the customer exists in the databse, used when logging in
def authenticate_customer(email_address_in, password_in):
    cursor = db.cursor()
    query = "SELECT * FROM Customer WHERE Customer.email_address = %s"
    try:
        cursor.execute(query, email_address_in)
        output = cursor.fetchall() # use .fetchone() becauause the query should only return one row, and not multipe rows
        # Note; type(output) is a list of length (only supports index 0). In this index is a dictionary of the row retrieved) output[0] to access dictionary,
        # output[0]["key_name"] to access the value in that key
        cursor.close()
        if output[0]["email_address"] == email_address_in and output[0]["password"] == password_in: # If the password_in matches the one retrieved # and output[0]["email_address"] == email_address_in: # if the email and password matches
            return True # return true
        if output[0]["email_address"] == email_address_in: # if only the email_address_in matches the one retrieved, account exists but wrong password
            # email exists, but password does not match what's stored in the database
            flash("Incorrect Password") # displays a temporary message for the user to see
            return False
        # Do not create a case for (output[0]["password"] == password_in)
        return False
    
    except Exception:
        flash("Incorrect Email")
        flash("Incorrect Password")
        return False # return False


# fucntion to check whether the airline staff exists in the databse, used when logging in
def authenticate_airline_staff(username_in, password_in):
    cursor = db.cursor()
    query = "SELECT * FROM Airline_Staff WHERE username = %s"
    
    try:
        cursor.execute(query, username_in)
        output = cursor.fetchall() # use .fetchone() becauause the query should only return one row, and not multipe rows
        cursor.close()

        if output[0]["password"] == password_in: # if the password matches
            return True # return true
        if output[0]["username"] == username_in:# if only the username_in matches the one retrieved, account exists but wrong password
            flash("Incorrect Username") # displays a temporary message for the user to see
            return False
        return False
    
    except Exception:
        flash("Incorrect Username")
        flash("Incorrect Password")
        return False


# function to check whether the airline staff already exists in the databse, used when registering
def airline_staff_exists(username_in):
    cursor = db.cursor()
    query = "SELECT * FROM Airline_Staff WHERE username = %s"
    
    try:
        cursor.execute(query, username_in)
        output = cursor.fetchall() # this query should only be returning one row becuase usernames are unique
        if output[0]["username"] == username_in: # if the retrieved output matches the username passed in 
            return True # return true becuase the username exists
        return False # if the usernames do not match, aka if it returns an empty set, the username doesn't exist
    
    except Exception:
        return False # erorr occured, couldn't check staff exists


# function to check whether the customer already exists in the databse, used when registering
def customer_exists(email_addess):
    cursor = db.cursor()
    query = "SELECT * FROM Customer WHERE email_address = %s"
    
    try:
        cursor.execute(query, (email_addess,)) # ust be email_address, because you have to pass in a tuple, not a single variable
        output = cursor.fetchall() # this query should only be returning one row becuase email_address are unique
        if output[0]["email_address"] == email_addess: # if the retrieved output matches the username passed in 
            return True # return true becuase the username exists
        return False # if the usernames do not match, aka if it returns an empty set, the username doesn't exist
    
    except Exception:
        return False# erorr occured, couldn't check customer exists

@app.route('/')
def index_page():
    # fetch()
    return render_template('index.html')

@app.route('/customer_login_page.html', methods = ['GET', 'POST']) # route to the customer's login page (Where they enter email and password)
def customer_login_page():
    if request.method == "POST":
        # Retrieve username and password from the form
        email = request.form['email_address']
        password = md5(request.form['password'].encode()).hexdigest()

        if (authenticate_customer(email, password)):
            session["email"] = email
            return redirect(url_for('customer')) # successful login, change url to load the customer page
            # return render_template('/customer_dashboard.html')
    
    # Authentication failed or method not POST
    # Redirect back to the login page with an error message
    return render_template('customer_login_page.html', error=True)



@app.route('/customer_dashboard.html', methods = ['GET', 'POST'])
def customer():
    try:

        email_address = session['email']
        cursor = db.cursor()
        query = "SELECT * FROM Customer where email_address = %s"
        cursor.execute(query, email_address)
        user_data = cursor.fetchall() # retrieves the data of the customer logged in
        
        query = """
        SELECT sum(Ticket.sold_price) 
        FROM Customer, Purchase, Ticket 
        WHERE Customer.email_address = %s and Customer.email_address = Purchase.email_address and Purchase.id_number = Ticket.id_number 
        and Purchase.purchase_date >= YEAR(DATE_SUB(CURDATE(), INTERVAL 1 YEAR))
        """
        # DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
        cursor.execute(query, email_address)
        user_spending = cursor.fetchall()[0]['sum(Ticket.sold_price)']
        
        query = """
        SELECT ticket.id_number, ticket.airline_name, ticket.flight_number, ticket.depart_date, ticket.depart_time 
        FROM purchase, ticket 
        WHERE purchase.email_address = %s and purchase.id_number = ticket.id_number;
        """
        cursor.execute(query, email_address)
        future_flights = cursor.fetchall()

        # return render_template('customer_dashboard.html')
        return render_template('customer_dashboard.html', customer = user_data[0], spendings_past_year = user_spending,future_flights=future_flights)

    except Exception:
        message = 'Please Login or Create an Account'
        return render_template('customer_login_page.html', error=message)


@app.route('/search_flights', methods = ['GET'])
def search_flights():
    if request.method == 'GET':
        email_address = session['email']
        airline_name = request.args.get('airline_name')
        flight_number = request.args.get('flight_number')
        depart_date = request.args.get('depart_date')
        depart_time = request.args.get('depart_time')
        
        cursor = db.cursor()
        query = "SELECT * FROM flight WHERE airline_name = %s AND flight_number = %s AND depart_date = %s AND depart_time = %s"
        
        cursor.execute(query, (airline_name, flight_number, depart_date, depart_time))
        found_flight = cursor.fetchall()
        
        query = "SELECT * FROM Customer where email_address = %s"
        cursor.execute(query, email_address)
        user_data = cursor.fetchall() # retrieves the data of the customer logged in
        
        query = """
        SELECT sum(Ticket.sold_price) 
        FROM Customer, Purchase, Ticket 
        WHERE Customer.email_address = %s and Customer.email_address = Purchase.email_address and Purchase.id_number = Ticket.id_number 
        and Purchase.purchase_date >= YEAR(DATE_SUB(CURDATE(), INTERVAL 1 YEAR))
        """
        # DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
        cursor.execute(query, email_address)
        user_spending = cursor.fetchall()[0]['sum(Ticket.sold_price)']
        
        query = """
        SELECT ticket.id_number, ticket.airline_name, ticket.flight_number, ticket.depart_date, ticket.depart_time 
        FROM purchase, ticket 
        WHERE purchase.email_address = %s and purchase.id_number = ticket.id_number;
        """
        cursor.execute(query, email_address)
        future_flights = cursor.fetchall()
        
        return render_template('customer_dashboard.html', customer = user_data[0], spendings_past_year = user_spending[0],future_flights=future_flights, found_flight=found_flight)


@app.route('/spending_range', methods=['GET'])
def spending_range():
    # try:
        email_address = session['email']
        cursor = db.cursor()
        
        # fetch user data:
        query = "SELECT * FROM Customer where Customer.email_address = %s"
        cursor.execute(query, email_address)
        user_data = cursor.fetchall() # extracts user data
        
        query = """
        SELECT sum(Ticket.sold_price) 
        FROM Customer, Purchase, Ticket 
        WHERE Customer.email_address = %s and Customer.email_address = Purchase.email_address and Purchase.id_number = Ticket.id_number 
        and Purchase.purchase_date >= YEAR(DATE_SUB(CURDATE(), INTERVAL 1 YEAR))
        """
        # DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
        cursor.execute(query, email_address)
        user_spending = cursor.fetchall()[0]['sum(Ticket.sold_price)']
        
        # fetch spending within a range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        query = """
        SELECT sum(Ticket.sold_price)
        FROM Customer, Purchase, Ticket 
        WHERE Customer.email_address = %s and Customer.email_address = Purchase.email_address and Purchase.id_number = Ticket.id_number 
        and Purchase.purchase_date >= %s and Purchase.purchase_date <= %s
        """
        cursor.execute(query, (email_address, start_date, end_date))
        range_spending = cursor.fetchall()[0]['sum(Ticket.sold_price)']
  
        query = """
        SELECT ticket.id_number, ticket.airline_name, ticket.flight_number, ticket.depart_date, ticket.depart_time 
        FROM purchase, ticket 
        WHERE purchase.email_address = %s and purchase.id_number = ticket.id_number;
        """
        cursor.execute(query, email_address)
        future_flights = cursor.fetchall()
        cursor.close()
        
        return render_template('customer_dashboard.html', customer = user_data[0], start_date=start_date, end_date=end_date, spending_past_year = user_spending, range_spending = range_spending, future_flights=future_flights)
    
    # except Exception as e:
    #     # Handle exceptions
    #     return "Error: Unable to fetch spending data within the specified range"
    
    
    
@app.route('/purchase_ticket', methods = ["POST"])   
def pay_for_ticket():
    if (request.method == "POST"):
        email_address = session['email']
        
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = request.form.get('date_of_birth')
        airline_name = request.form.get('airline_name')
        flight_number = request.form.get('flight_number')
        depart_date = request.form.get('depart_date')
        depart_time = request.form.get('depart_time')
        card_type = request.form.get('card_type')
        card_number = md5(request.form.get('card_number').encode()).hexdigest()
        name_on_card = request.form.get('name_on_card')
        expiration_date = request.form.get('expiration_date')
        
        if (check_if_flight_exists(airline_name, flight_number, depart_date, depart_time)):
            curs = db.cursor()
            query1 = "SELECT base_price FROM flight WHERE airline_name = %s AND flight_number = %s AND depart_date = %s AND depart_time = %s"
            query2 = "SELECT airplane_id_number FROM flight WHERE airline_name = %s AND flight_number = %s AND depart_date = %s AND depart_time = %s"
            query3 = "SELECT COUNT(id_number) FROM ticket WHERE airline_name = %s AND flight_number = %s AND depart_date = %s AND depart_time = %s"
            query4 = "SELECT num_of_seat FROM airplane WHERE id_number = %s AND airline_name = %s"
            
            curs.execute(query1, (airline_name, flight_number, depart_date, depart_time))
            price = curs.fetchall()[0]['base_price']

            curs.execute(query2, (airline_name, flight_number, depart_date, depart_time))
            airplane_id = curs.fetchall()[0]['airplane_id_number']
            
            curs.execute(query3, (airline_name, flight_number, depart_date, depart_time))
            num_of_taken_seats = curs.fetchall()[0]['COUNT(id_number)']
            
            curs.execute(query4, (airplane_id, airline_name))
            num_of_total_seats = curs.fetchall()[0]['num_of_seat']
            
            if (num_of_taken_seats / num_of_total_seats) >= 0.8 & (num_of_taken_seats / num_of_total_seats) < 1:
                price = price *.75
            elif (num_of_taken_seats / num_of_total_seats) == 1:
                curs.close()
                error = "ERROR: FLIGHT IS FULL"
                return redirect(url_for('customer'))
            
            query5 = "SELECT COUNT(id_number) FROM ticket"
            curs.execute(query5)

            id_number = curs.fetchall()[0]['COUNT(id_number)'] + 100
            query6 = "INSERT INTO ticket VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            query7 = "INSERT INTO purchase VALUES (%s, %s, CURTIME(), CURDATE(), %s, %s, %s, %s)"
            
            curs.execute(query6, (id_number, airline_name, flight_number, depart_date, depart_time, price, first_name, last_name, dob))
            curs.execute(query7, (id_number, email_address, card_type, card_number, name_on_card, expiration_date))
            
            db.commit()
            curs.close()
            
            return redirect(url_for('customer'))
            
@app.route('/cancel_ticket', methods = ["GET", "POST"])
def cancel_trip():
    if (request.method == "POST"):
        ticket_id = request.form.get('ticket_id')
        
        curs = db.cursor()
        query1 = "SELECT * FROM ticket WHERE id_number = %s"
        
        curs.execute(query1, (ticket_id))
        output = curs.fetchall()
        output_exists = output != {}
        
        # dobj = datetime.strptime(output[0]['depart_date'], "%Y-%m-%d").date()
        dobj = output[0]['depart_date']
        current_date = date.today()
        in_future = current_date < dobj
        
        if (output_exists & in_future):
            query2 = "DELETE FROM Ticket WHERE id_number = %s"
            query3 = "DELETE FROM Purchase WHERE id_number = %s"
            query4 = "DELETE FROM Trips WHERE outbound_ticket_id = %s OR return_ticket_id = %s"
            
            curs.execute(query4, (ticket_id, ticket_id))
            curs.execute(query2, (ticket_id))
            curs.execute(query3, (ticket_id))

            db.commit()
            curs.close()
            
            return redirect(url_for('customer'))
        else:
            curs.close()
            error = "ERROR: Ticket does not exist!"
            return redirect(url_for('customer'))
    else:
        return redirect(url_for('customer'))


@app.route('/airline_staff_login_page.html', methods = ['GET', 'POST']) # route to the arline staff's login page (Where they enter email and password)
def airline_staff_login_page():
    if request.method == "POST":
        username = request.form['username']
        password = md5(request.form['password'].encode()).hexdigest()
    
        if (authenticate_airline_staff(username, password)):
            session["username"] = username
            return redirect(url_for('airline_staff'))  # successful login, change url to load the airline staff page
            # return render_template('/airline_staff_board.html')
    
    # Authentication failed or method not POST
    # Redirect back to the login page with an error message
    return render_template('airline_staff_login_page.html', error=True)

@app.route('/airline_staff_board.html', methods = ['GET', 'POST'])
def airline_staff():
    try:
        username = session["username"]
        cursor = db.cursor()
        
        # fetch staff data
        query = "SELECT * FROM Airline_Staff WHERE Airline_Staff.username = %s"
        cursor.execute(query, username)
        user_data = cursor.fetchall() # gets the airline staff info from the Airline_Staff table

        query = " SELECT * FROM Employed_By where username = %s"
        cursor.execute(query, username)
        output = cursor.fetchall()
        airline_name = output[0]["airline_name"] # gets the airline name the airline staff works for
        
        query = """
        SELECT *
        FROM Flight
        WHERE Flight.airline_name = %s and Flight.depart_date > CURDATE()
        """
        cursor.execute(query, airline_name)
        # a list of dictionaries; each dictionary holds information about the flight where the ailine matches what the staff works for
        # and, each dictionary contains a future flight
        output2 = cursor.fetchall() # gets all future flights in which the airline staff works for
    
        
        query = """
        SELECT Reviews.airline_name, Reviews.flight_number, Reviews.depart_date, Reviews.depart_time, Reviews.rating, Reviews.comment 
        FROM Reviews, Flight 
        WHERE Reviews.airline_name = %s and Reviews.flight_number = Flight.flight_number and Reviews.depart_date = Flight.depart_date and 
        Reviews.depart_time = Flight.depart_time;
        """
        
        cursor.execute(query, airline_name)
        reviews = cursor.fetchall() # a list of dictionaries
        
        query= """
        SELECT MAX(purchase_count), email_address 
        FROM (SELECT COUNT(Purchase.id_number) as purchase_count, Purchase.email_address 
                FROM Purchase INNER JOIN Ticket ON Purchase.id_number = Ticket.id_number 
                WHERE Ticket.airline_name = %s 
                GROUP BY Purchase.id_number, Purchase.email_address) 
        AS PurchaseCounts GROUP BY email_address;
        """
        
        cursor.execute(query, airline_name)
        output = cursor.fetchall()
        
        if output:
            ticket_count = output[0]['MAX(purchase_count)']
            customer_email = output[0]['email_address']
            query="""
            SELECT *
            FROM Customer
            WHERE email_address = %s
            """
            cursor.execute(query, customer_email)
            output = cursor.fetchall()
            customer_info = output[0]
        
        return render_template('airline_staff_dashboard.html', staff = user_data[0], airline_name = airline_name, future_flights = output2, reviews = reviews, ticket_count = ticket_count, customer_info = customer_info)
    
    except:
        message = 'Please Login or Create an Account'
        # return render_template('airline_staff_dashboard.html', user_data = user_data[0], airline_name = airline_name, future_flights = output2)
        return render_template('airline_staff_login_page.html', error=message)

def check_if_flight_exists(airline, flight_num, depart_date, depart_time):
    curs = db.cursor()
    query = "SELECT * FROM flight WHERE airline_name = %s AND flight_number = %s AND depart_date = %s AND depart_time = %s"
    
    try:
        output = curs.execute(query, (airline, flight_num, depart_date, depart_time))
        output = curs.fetchall()
        if output:
            return True
        else:
            return False
    except:
        return False

@app.route('/add_flight', methods = ["GET", "POST"])
def create_flight():
    if (request.method == "POST"):
        flight_number = request.form.get('flight_number')
        departing_airport_code = request.form.get('depart_airport_code')
        depart_date = request.form.get('depart_date')
        depart_time = request.form.get('depart_time')
        destination_airport_code = request.form.get('arrival_airport_code')
        arrival_date = request.form.get('arrival_date')
        arrival_time = request.form.get('arrival_time')
        base_price = request.form.get('base_price')
        status = request.form.get('status')
        airplane_id_number = request.form.get('airplane_id')
        
        dobj = datetime.strptime(depart_date, "%Y-%m-%d").date()
        current_date = date.today()
        in_future = current_date < dobj
        
        curs = db.cursor()
        query1 = "INSERT INTO flight VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        
        query2 = " SELECT * FROM Employed_By where username = %s"
        curs.execute(query2, session.get('username'))
        output = curs.fetchall()
        airline_name = output[0]["airline_name"]
                
        if (not (check_if_flight_exists(airline_name, flight_number, depart_date, depart_time))) and in_future:
            curs.execute(query1, (airline_name, flight_number, depart_date, depart_time, departing_airport_code, arrival_date, arrival_time, destination_airport_code, base_price, status, airplane_id_number))
            db.commit()
            curs.close()
            return redirect(url_for('airline_staff'))
        else:
            curs.close()
            error = "Flight already exists"
            return redirect(url_for('airline_staff'))
    else:
        return redirect(url_for('airline_staff'))

@app.route('/change_flight_status', methods = ["GET","POST"])
def change_flight_status():
    if (request.method == "POST"):
        flight_number = request.form.get('flight_number')
        depart_date = request.form.get('depart_date')
        depart_time = request.form.get('depart_time')
        status = request.form.get('status')
        
        curs = db.cursor()
        query1 = "UPDATE Flight SET status = %s WHERE airline_name = %s AND flight_number = %s AND depart_date = %s AND depart_time = %s"
        
        query2 = " SELECT * FROM Employed_By where username = %s"
        curs.execute(query2, session.get('username'))
        output = curs.fetchall()
        airline_name = output[0]["airline_name"]
                
        if (check_if_flight_exists(airline_name, flight_number, depart_date, depart_time)):
            curs.execute(query1, (status, airline_name, flight_number, depart_date, depart_time))
            db.commit()
            curs.close()
            return redirect(url_for('airline_staff'))
        else:
            curs.close()
            error = "ERROR: Flight does not exist"
            return redirect(url_for('airline_staff'))
    else:
        return redirect(url_for('airline_staff'))

def check_airport_exists(code):
    curs = db.cursor()
    query = "SELECT * FROM Airport WHERE code = %s"
    
    try:
        curs.execute(query, (code))
        output = curs.fetchall()
        if (output):
            return True
        else:
            return False
    except:
        return False

@app.route('/add_airport', methods = ["POST"])
def add_airport():
    if (request.method == "POST"):
        code = request.form.get('code')
        name = request.form.get('name')
        city = request.form.get('city')
        country = request.form.get('country')
        number_of_terminals = request.form.get('number_of_terminals')
        type = request.form.get('type')
        
        
        curs = db.cursor()
        query1 = "INSERT INTO airport VALUES (%s, %s, %s, %s, %s, %s)"
        
        if not (check_airport_exists(code)):
            curs.execute(query1, (code, name, city, country, number_of_terminals, type))
            db.commit()
            curs.close()
            return redirect(url_for('airline_staff'))
        else:
            curs.close()
            error = "Airport already exists!"
            return redirect(url_for('airline_staff'))
    else:
        return redirect(url_for('airline_staff'))

def check_airplane_exists(airline_name, id):
    curs = db.cursor()
    query = "SELECT * FROM Airplane WHERE airline_name = %s AND id = %s"
    
    try:
        curs.execute(query, (airline_name, id))
        output = curs.fetchall()
        if output:
            return True
        else:
            return False
    except:
        return False

#missing maintenance id in airplane sql
#missing airline name in airline staff dashboard html
@app.route('/add_airplane', methods = ['POST'])
def add_airplane():
    if (request.method == "POST"):
        id_number = request.form.get('id_number')
        number_of_seats = request.form.get('num_of_seats')
        manufacturing_company = request.form.get('manufacturing_company')
        model_number = request.form.get('model_number')
        manufacturing_date = request.form.get('manufacturing_date')
        age = request.form.get('age')
        
        curs = db.cursor()
        query1 = "INSERT INTO Airplane VALUES (%s, %s, NULL, %s, %s, %s, %s, %s)"
        
        query2 = " SELECT * FROM Employed_By where username = %s"
        curs.execute(query2, session.get('username'))
        output = curs.fetchall()
        airline_name = output[0]["airline_name"]
        
        if not check_airplane_exists(airline_name, id_number):
            curs.execute(query1, (airline_name, id_number, number_of_seats, manufacturing_company, model_number, manufacturing_date, age))
            db.commit()
            curs.close()
            return redirect(url_for('airline_staff'))
        else:
            curs.close()
            error = "Airplane already exists!"
            return redirect(url_for('airline_staff'))
    else:
        return redirect(url_for('airline_staff'))

def maintenance_exists(id):
    curs = db.cursor()
    query = "SELECT * FROM Maintenance WHERE id = %s"
    
    try:
        output = curs.execute(query, (id))
        if (output[0] == id):
            return True
        else:
            return False
    except:
        return False

@app.route('/schedule_maintenance', methods = ['POST'])
def schedule_maintenance():
    if (request.method == "POST"):
        airplane_id = request.form.get('airplane_id')
        id = request.form.get('maintenance_id')
        start_date = request.form.get('start_date')
        start_time = request.form.get('start_time')
        end_date = request.form.get('end_date')
        end_time = request.form.get('end_time')
        
        curs = db.cursor()
        query1 = "INSERT INTO Maintenance VALUES (%s, %s, %s, %s, %s)"
        query2 = "UPDATE Airplane SET maintenance_id = %s WHERE airline_name = %s AND id_number = %s"
        
        query3 = " SELECT * FROM Employed_By where username = %s"
        curs.execute(query3, session.get('username'))
        output = curs.fetchall()
        airline_name = output[0]["airline_name"]
        
        if not (maintenance_exists(id)):
            curs.execute(query1, (id, start_date, start_time, end_date, end_time))
            curs.execute(query2, (id, airline_name, airplane_id))
            db.commit()
            curs.close()
            return redirect(url_for('airline_staff'))
        else:
            curs.close()
            error = "ERROR: Maintenance already exists!"
            return redirect(url_for('airline_staff'))
    else:
        return redirect(url_for('airline_staff'))

@app.route('/rating.html', methods = ['GET'])
def ratings():
    if request.method == "GET":
        try:
            if (session['email']):
                return render_template('rating.html')
        except:
            return render_template('customer_dashboard.html')

    return render_template('customer_dashboard.html')


@app.route('/submit_rating', methods=['POST'])
def submit_ratings():
    if request.method == 'POST':
        # Retrieve form data
        email_address = session['email']
        airline_name = request.form['airline_name']
        flight_number = request.form['flight_number']
        depart_date = request.form['depart_date']
        depart_time = request.form['depart_time']
        rating = request.form['rating']
        comments = request.form['comments']
        cursor = db.cursor()
        if 'email' not in session:
            return redirect(url_for('customer'))
        query = """
        SELECT * 
        FROM Flight 
        WHERE airline_name = %s and flight_number = %s and depart_date = %s and depart_time = %s and depart_date < CURRENT_DATE() and  depart_date < CURRENT_TIME()
        """
        cursor.execute(query, (airline_name, flight_number, depart_date, depart_time))

        output = cursor.fetchall()
        
        if not output: # query returned nothing, meaning flight doesnt exist
            return render_template('rating.html')
        
        query = """
        INSERT INTO Reviews (email_address, airline_name, flight_number, depart_date, depart_time, rating, comment) values (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (email_address, airline_name, flight_number, depart_date, depart_time, rating, comments))
        
        db.commit()
        cursor.close()
        
        return redirect(url_for('customer'))
     
    return redirect(url_for('customer'))
            
@app.route("/registration_for_airline_staff_page.html", methods = ["GET", "POST"])
def register_airline_staff():
    if (request.method == "POST"):
        username = request.form.get('username')
        password = md5(request.form.get('password').encode()).hexdigest()
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = request.form.get('date_of_birth')
        phone_number = request.form.get('phone_number')
        email_address = request.form.get('email_address')
        airline_name = request.form.get('airline_name')
        
        curs = db.cursor()
        query1 = "INSERT INTO airline_staff VALUES (%s, %s, %s, %s, %s)"
        query2 = "INSERT INTO airline_staff_email_address VALUES (%s, %s)"
        query3 = "INSERT INTO airline_staff_phone_number VALUES (%s, %s)"
        query4 = "INSERT INTO employed_by VALUES (%s, %s)"
           
        if not (airline_staff_exists(username)):
            curs.execute(query1, (username, password, first_name, last_name, dob))
            curs.execute(query2, (username, email_address))
            curs.execute(query3, (username, phone_number))
            curs.execute(query4, (airline_name, username))
            
            db.commit()
            curs.close()
            return render_template('airline_staff_login_page.html')
        else:
            curs.close()
            error = "ERROR: Airline Staff Member Already Exists!"
            return render_template('registration_for_airline_staff_page.html', error=error)
    else:
        return render_template('registration_for_airline_staff_page.html')
    
@app.route("/registration_for_customer_page.html", methods = ["GET", "POST"])
def register_customer():
    if (request.method == "POST"):
        email_address = request.form.get('email_address')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = md5(request.form.get('password').encode()).hexdigest()
        building_number = request.form.get('building_number')
        street = request.form.get('street')
        apt_number = request.form.get('apt_number')
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zipcode')
        phone_number = request.form.get('phone_number')
        passport_number = request.form.get('passport_number')
        passport_expiration = request.form.get('passport_expiration')
        passport_country = request.form.get('passport_country')
        dob = request.form.get('date_of_birth')
        
        curs = db.cursor()
        query1 = "INSERT INTO customer VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        query2 = "INSERT INTO customerphone VALUES (%s, %s)"
           
        if not (customer_exists(email_address)):
            curs.execute(query1, (email_address, first_name, last_name, password, building_number,street, apt_number, city, state, zipcode, passport_number, passport_expiration, passport_country, dob))            
            curs.execute(query2, (email_address, phone_number))
            
            db.commit()
            curs.close()
            return render_template('customer_login_page.html')
        else:
            curs.close()
            error = "ERROR: Customer Already Exists!"
            return render_template('registration_for_customer_page.html', error=error)
    else:
        return render_template('registration_for_customer_page.html')
            
@app.route('/customer_logout', methods=['GET'])
def customer_logout():
    # Clear the session data
    session.pop('email', None)
    # Redirect to the customer login page
    return render_template('index.html')

@app.route('/airline_staff_logout', methods=['GET'])
def airline_staff_logout():
    # Clear the session data
    session.pop('username', None)
    # Redirect to the airline staff login page
    return render_template('index.html')
        
if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug = True)
    
