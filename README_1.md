# Airline_Ticketing_System
This repository mimics is a CRUD application that allows for the booking, cancelling, and enrolling of new customers/airline staff. This project was broken up into mainly three parts: Client-side, Server-side, and Database

1) Client-Side (Frontend):
   - HTML templates were used and rendered via Flask
   - Users are able to interact with and enter information to HTML pages
   - When a user submits a form, it is sent over via HTTP requests to the server

2) Server-Side (Backend):
   - The Flask framework was used to implement the server-side, handling form requests
   - Processes the HTTP requests (GET/POST), and also interacts with the MySQL database via pymysql
   - Returns rendered HTML template to client, or redirects client to other routes
   - Uses flask.session to keep track of current session
  
3) Database (Storage):
   - Uses MySQL to store data (relational database)
   - Connected to server via pymysql
