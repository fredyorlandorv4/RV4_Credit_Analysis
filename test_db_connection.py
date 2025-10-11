#!/usr/bin/env python3
"""
Test script to verify PostgreSQL database connection
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db, Application
from app_updated import app
import psycopg2
from sqlalchemy import text

def test_direct_connection():
    """Test direct PostgreSQL connection"""
    print("1. Testing direct PostgreSQL connection...")
    
    try:
        # Test with local connection
        conn = psycopg2.connect(
            host="192.227.80.200",
            port=27018,
            database="app",
            user="app_user",
            password="rvH~}f781{}["
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Direct connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Direct connection failed: {e}")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection"""
    print("\n2. Testing SQLAlchemy connection...")
    
    try:
        with app.app_context():
            # Test basic connection
            result = db.session.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ SQLAlchemy connection successful!")
            print(f"PostgreSQL version: {version}")
            
            # Test if we can query existing tables
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"✅ Found {len(tables)} existing tables:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("ℹ️  No tables found - database appears to be empty")
            
            return True
            
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False

def test_table_creation():
    """Test table creation and database schema setup"""
    print("\n3. Testing table creation...")
    
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Tables created successfully!")
            
            # Check that tables were created
            result = db.session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = result.fetchall()
            
            if tables:
                print(f"✅ Found {len(tables)} tables after creation:")
                for table in tables:
                    print(f"  - {table[0]}")
            
            print("✅ Database schema setup completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Table creation/operations failed: {e}")
        return False

def main():
    print("PostgreSQL Database Connection Test")
    print("=" * 50)
    
    # Test 1: Direct connection
    direct_success = test_direct_connection()
    
    # Test 2: SQLAlchemy connection
    sqlalchemy_success = test_sqlalchemy_connection()
    
    # Test 3: Table operations (only if SQLAlchemy works)
    table_success = False
    if sqlalchemy_success:
        table_success = test_table_creation()
    
    # Summary
    print("\n" + "=" * 50)
    print("CONNECTION TEST SUMMARY:")
    print(f"Direct PostgreSQL connection: {'✅ PASS' if direct_success else '❌ FAIL'}")
    print(f"SQLAlchemy connection: {'✅ PASS' if sqlalchemy_success else '❌ FAIL'}")
    print(f"Table operations: {'✅ PASS' if table_success else '❌ FAIL'}")
    
    if direct_success and sqlalchemy_success and table_success:
        print("\n🎉 All tests passed! Database is ready for use.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)