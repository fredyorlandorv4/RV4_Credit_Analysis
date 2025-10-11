#!/usr/bin/env python3
"""
Database migration to allow NULL application_id in activity_logs
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app_updated import app, db
from database import ActivityLog

def migrate_activity_logs():
    """Update activity_logs table to allow NULL application_id"""
    with app.app_context():
        try:
            # Execute raw SQL to modify the column
            db.engine.execute("""
                ALTER TABLE activity_logs 
                MODIFY COLUMN application_id INT NULL
            """)
            
            print("✅ Successfully updated activity_logs table to allow NULL application_id")
            return True
            
        except Exception as e:
            print(f"❌ Migration error: {e}")
            
            # Try alternative approach for different database engines
            try:
                db.engine.execute("""
                    ALTER TABLE activity_logs 
                    ALTER COLUMN application_id DROP NOT NULL
                """)
                print("✅ Successfully updated activity_logs table (alternative method)")
                return True
            except Exception as e2:
                print(f"❌ Alternative migration error: {e2}")
                
                # For SQLite or other databases that don't support column modification
                print("⚠️  Column modification not supported. Will handle in application logic.")
                return False

if __name__ == '__main__':
    migrate_activity_logs()
