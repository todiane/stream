# db_test.py
import os
import MySQLdb
import environ
from pathlib import Path
import socket

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# Initialize environ
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


def test_db_connection():
    try:
        # Print connection details
        print("\nAttempting to connect to database with following settings:")
        print(f"Host: {env('DATABASE_HOST')}")
        print(f"Database: {env('DATABASE_NAME')}")
        print(f"User: {env('DATABASE_USER')}")
        print(f"Port: {env('DATABASE_PORT', default='3306')}")

        # Try to resolve hostname first
        try:
            host_ip = socket.gethostbyname(env("DATABASE_HOST"))
            print(f"\nHost resolves to IP: {host_ip}")
        except socket.gaierror as e:
            print(f"\nWarning: Could not resolve hostname: {str(e)}")

        print("\nAttempting connection...")
        connection = MySQLdb.connect(
            host=env("DATABASE_HOST"),
            user=env("DATABASE_USER"),
            passwd=env("DATABASE_PASSWORD"),
            db=env("DATABASE_NAME"),
            port=int(env("DATABASE_PORT", default="3306")),
        )
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"Successfully connected to MariaDB. Version: {version[0]}")

        # Test a basic query
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\nAvailable tables:")
        for table in tables:
            print(f"- {table[0]}")

        connection.close()
        return True
    except Exception as e:
        print(f"\nError connecting to database: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check if the hostname is correct in your .env file")
        print("2. Verify that your IP is allowed in 20i's database security settings")
        print("3. Confirm the database credentials are correct")
        return False


if __name__ == "__main__":
    test_db_connection()
