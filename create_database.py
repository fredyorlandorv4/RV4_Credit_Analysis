#!/usr/bin/env python3
"""
Script to create the credit_dashboard database if it doesn't exist
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

def create_database():
    """Create credit_dashboard database if it doesn't exist"""
    
    # Database connection parameters
    host = "192.227.80.200"
    port = 27018
    user = "app_user"
    password = "rvH~}f781{}["
    database_name = "credit_dashboard"
    
    try:
        # First, connect to PostgreSQL server (not to a specific database)
        # Use 'postgres' as the default database to connect to
        print("Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"  # Connect to default postgres database first
        )
        
        # Set autocommit mode for database creation
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (database_name,))
        exists = cursor.fetchone()
        
        if exists:
            print(f"Database '{database_name}' already exists.")
        else:
            # Create the database
            print(f"Creating database '{database_name}'...")
            cursor.execute(f'CREATE DATABASE "{database_name}"')
            print(f"Database '{database_name}' created successfully!")
        
        cursor.close()
        conn.close()
        
        # Now test connection to the new database
        print(f"Testing connection to '{database_name}'...")
        test_conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database_name
        )
        test_conn.close()
        print(f"Successfully connected to '{database_name}'!")
        
        return True
        
    except psycopg2.Error as e:
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = create_database()
    if success:
        print("\nDatabase setup completed successfully!")
        print("You can now update your application configuration to use 'credit_dashboard' database.")
    else:
        print("\nDatabase setup failed!")
        sys.exit(1)