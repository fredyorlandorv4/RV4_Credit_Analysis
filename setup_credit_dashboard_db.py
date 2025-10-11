#!/usr/bin/env python3
"""
Script to create the credit_dashboard database using admin privileges
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import getpass

def create_database_as_admin():
    """Create credit_dashboard database as admin user"""
    
    # Database connection parameters
    host = "192.227.80.200"
    port = 27018
    database_name = "credit_dashboard"
    app_user = "app_user"
    
    print("Creating credit_dashboard database...")
    print("This script will try different admin users to create the database.")
    
    # Common admin usernames to try
    admin_users = ["postgres", "admin", "root", "doadmin"]
    
    for admin_user in admin_users:
        try:
            print(f"\nTrying to connect as '{admin_user}'...")
            password = getpass.getpass(f"Enter password for {admin_user}: ")
            
            # Connect to PostgreSQL server
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=admin_user,
                password=password,
                database="postgres"  # Connect to default postgres database
            )
            
            # Set autocommit mode for database creation
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (database_name,))
            exists = cursor.fetchone()
            
            if exists:
                print(f"✅ Database '{database_name}' already exists.")
            else:
                # Create the database
                print(f"Creating database '{database_name}'...")
                cursor.execute(f'CREATE DATABASE "{database_name}"')
                print(f"✅ Database '{database_name}' created successfully!")
            
            # Grant privileges to app_user
            print(f"Granting privileges to '{app_user}'...")
            cursor.execute(f'GRANT ALL PRIVILEGES ON DATABASE "{database_name}" TO "{app_user}"')
            print(f"✅ Privileges granted to '{app_user}'!")
            
            cursor.close()
            conn.close()
            
            # Test connection as app_user
            print(f"Testing connection as '{app_user}'...")
            test_conn = psycopg2.connect(
                host=host,
                port=port,
                user=app_user,
                password="rvH~}f781{[",
                database=database_name
            )
            test_conn.close()
            print(f"✅ Successfully connected as '{app_user}' to '{database_name}'!")
            
            return True
            
        except psycopg2.Error as e:
            print(f"❌ Failed with user '{admin_user}': {e}")
            continue
        except KeyboardInterrupt:
            print("\\n❌ Operation cancelled by user.")
            return False
        except Exception as e:
            print(f"❌ Unexpected error with user '{admin_user}': {e}")
            continue
    
    print("\\n❌ Could not create database with any admin user.")
    return False

def alternative_approach():
    """Alternative approach - rename existing 'app' database"""
    print("\\nAlternative approach: Rename existing 'app' database to 'credit_dashboard'")
    print("This requires admin privileges and will rename the existing database.")
    
    response = input("Do you want to try this approach? (y/N): ")
    if response.lower() != 'y':
        return False
    
    # This would require admin privileges too, so same issue
    print("This approach also requires admin privileges.")
    return False

def main():
    print("Credit Dashboard Database Setup")
    print("=" * 50)
    
    success = create_database_as_admin()
    
    if not success:
        print("\\nAlternatively, you can:")
        print("1. Ask your database administrator to create the 'credit_dashboard' database")
        print("2. Use the existing 'app' database (change the config back)")
        print("3. Use a local SQLite database for development")
        
        # Offer to revert to 'app' database
        response = input("\\nWould you like to revert to using the 'app' database? (y/N): ")
        if response.lower() == 'y':
            return 'revert'
    
    return success

if __name__ == "__main__":
    result = main()
    if result == 'revert':
        print("Please manually change the database name back to 'app' in app_updated.py")
    elif result:
        print("\\n🎉 Database setup completed successfully!")
    else:
        print("\\n❌ Database setup failed!")
        sys.exit(1)