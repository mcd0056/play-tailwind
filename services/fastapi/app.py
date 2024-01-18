from fastapi import FastAPI
from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.sql import select

DATABASE_URL = "postgresql://postgres:1234@db:5432/postgres"

# Database table definitions
metadata = MetaData()
users = Table(
    "user", 
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50)),
    Column("email", String(120)),
    Column('openai_api_key', String(200))
)

# FastAPI app initialization
app = FastAPI()

# Database instance
database = Database(DATABASE_URL)

@app.on_event("startup")
async def startup():
    await database.connect()
    # Initialize database schema (create tables)
    engine = create_engine(DATABASE_URL)
    metadata.create_all(engine)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/users/")
async def read_users():
    query = users.select()
    return await database.fetch_all(query)

@app.get("/users/{user_id}")
async def read_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    return await database.fetch_one(query)


