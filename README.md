Execute python file inside docker 

docker exec -it play-tailwind-flask_app-1 python start_db.py

List All Databases:
\l

Connect to a Specific Database:
\c <database_name>

List All Tables in the Current Database:
\dt

Describe a Table (to see the structure of the table):
\d <table_name>

List All Users/Roles:
\du


Run a Query (example: select everything from a table):


SELECT * FROM <table_name>;
Exit psql:


\q


docker exec -it play-tailwind-db-1 psql -U postgres postgres

http://flask_app.localhost:81
http://fastapi.localhost:81