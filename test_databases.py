#!/usr/bin/env python3
"""
Script to test database connections and list available databases
"""

import psycopg2
import sys

def test_database_connection():
    """Test connection to different databases and list available ones"""
    
    # Database connection parameters
    host = "192.227.80.200"
    port = 27018
    user = "app_user"
    password = "rvH~}f781{}["
    
    # Test different database names
    databases_to_test = ["app", "credit_dashboard", "postgres", "defaultdb"]
    
    print("Testing database connections...")
    print("-" * 50)
    
    working_databases = []
    
    for db_name in databases_to_test:
        try:
            print(f"Testing connection to '{db_name}'...")
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=db_name
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✓ Successfully connected to '{db_name}'")
            print(f"  PostgreSQL version: {version[0][:50]}...")
            
            cursor.close()
            conn.close()
            working_databases.append(db_name)
            
        except psycopg2.Error as e:
            print(f"✗ Failed to connect to '{db_name}': {e}")
    
    print("\n" + "=" * 50)
    if working_databases:
        print(f"Working databases: {', '.join(working_databases)}")
        
        # Try to list all databases using the first working connection
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=working_databases[0]
            )
            cursor = conn.cursor()
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            all_databases = cursor.fetchall()
            
            print("\nAll available databases:")
            for db in all_databases:
                print(f"  - {db[0]}")
                
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Could not list databases: {e}")
            
    else:
        print("No working database connections found!")
        return False
    
    return True

if __name__ == "__main__":
    success = test_database_connection()
    if not success:
        sys.exit(1)