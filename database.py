# Asynchronous is being used --- good for scalability 
# this is the file for connecting the sqlachemy models to the database
# in this file the Asynchronous engine is created
# a lot in this file right now is for testing and debugging purposes only 
#      I needed to make sure the connections were working and the Asynchronus engine was working right 
# need to instail aiomysql library 
# need to install greenlet library 
# instal newest SQLalchemy 
import models
import asyncio
#from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select  # Import `select` to handle queries properly

# Database connection details
# this is the local connection using my local SQL server and SQL workbench 
hostname = "localhost"
username = "root"
password = "root!!**"
port = 3306
database = "app_db"

# Connection URL for SQLAlchemy (async)
SQLALCHEMY_DATABASE_URL = f"mysql+aiomysql://{username}:{password}@{hostname}:{port}/{database}"

# Create an asynchronous engine instance
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    echo=True, # Log all SQL queries for debugging
    pool_size=10,  # Initial pool size is 10 connections
    max_overflow=20  # Allow 20 overflow connections if needed
)

# Create an asynchronous sessionmaker
AsyncSessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Dependency for obtaining a session (asynchronous)
async def get_db():
    # Using context manager to ensure session is closed correctly
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()  # Explicitly close the session after use

# Function to create tables asynchronously
async def create_tables():
    try:
        async with engine.begin() as conn:
            # Use run_sync to execute the synchronous `create_all()` method
            await conn.run_sync(models.Base.metadata.create_all)
            print("Tables created successfully!")
    except SQLAlchemyError as e:
        print(f"Error creating tables: {e}")

# Test the connection (asynchronous)
async def test_connection():
    try:
        # Try to connect to the database asynchronously
        async with engine.connect() as connection:
               # Execute a simple query to test connection
            result = await connection.execute(select(1))
            print("Connection to the database was successful!")
            print(result.fetchall())  # Optional: Print the result
    except SQLAlchemyError as e:
        print("Error connecting to the database:", e)

# Test the connection (asynchronous) using the `medication` table
async def get_medication():
    try:
        async with AsyncSessionLocal() as session:  # Use the session directly here
            result = await session.execute(select(models.Medication))  
            medications = result.scalars().all()  # Extract the rows as a list

            print(f"Found {len(medications)} medications:")
            for med in medications:
                print(med)  # Print the custom string representation of the Medication object
    except SQLAlchemyError as e:
        print(f"Error retrieving medications: {e}")

# have to use this method "close_connections" to avoid the "RuntimeError: Event loop is closed" in Python 3.12 
async def close_connections():
    # Ensure connections are explicitly closed before exiting
    await engine.dispose()
    print("Connections closed.")
    # Ensures no nested event loops or calls to asyncio.run() that can close the event loop prematurely.
  
async def main():
    try:
        # Run the functions using asyncio
        await create_tables()  # Create tables
        await test_connection()  # Test the connection
        await get_medication()  # Fetch medication data
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await close_connections()  # Close connections

# Run the main function within asyncio.run to ensure proper event loop management
if __name__ == "__main__":
    # Ensure asyncio.run() is used correctly to avoid event loop issues in Python 3.12
  # Ensure asyncio.run() is only called once to avoid event loop closure issues
    try:
        asyncio.run(main())  # Only one asyncio.run() should be called in the program
    except RuntimeError as e:
        print("Caught RuntimeError: Event loop is closed")


