"""
Migration script to add tenant_id to existing documents
Run this after implementing multi-tenancy
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.base import (
    clients_collection,
    projects_collection,
    services_collection,
    invoices_collection,
    payments_collection,
    files_collection,
    companies_collection,
    user_company_roles_collection
)
from datetime import datetime
from uuid import uuid4


def create_default_company():
    """Create a default company for existing data"""
    # Check if default company exists
    default_company = companies_collection.find_one({"name": "Default Company"})
    
    if not default_company:
        company_id = uuid4().hex
        company_doc = {
            "id": company_id,
            "name": "Default Company",
            "email": "admin@defaultcompany.com",
            "subscription_plan": "free",
            "subscription_status": "active",
            "is_active": True,
            "max_users": 100,
            "max_projects": 1000,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        companies_collection.insert_one(company_doc)
        print(f"✅ Created default company with ID: {company_id}")
        return company_id
    else:
        print(f"✅ Default company already exists with ID: {default_company['id']}")
        return default_company['id']


def add_tenant_id_to_collection(collection, collection_name, tenant_id):
    """Add tenant_id to all documents in collection that don't have it"""
    # Count documents without tenant_id
    count_without = collection.count_documents({"tenant_id": {"$exists": False}})
    
    if count_without == 0:
        print(f"✅ {collection_name}: All documents already have tenant_id")
        return
    
    # Update all documents
    result = collection.update_many(
        {"tenant_id": {"$exists": False}},
        {"$set": {"tenant_id": tenant_id}}
    )
    
    print(f"✅ {collection_name}: Added tenant_id to {result.modified_count} documents")


def run_migration():
    """Run the migration"""
    print("🚀 Starting multi-tenancy migration...")
    print("=" * 60)
    
    # Step 1: Create default company
    print("\n📦 Step 1: Creating default company...")
    default_tenant_id = create_default_company()
    
    # Step 2: Add tenant_id to all collections
    print("\n📦 Step 2: Adding tenant_id to existing data...")
    
    collections_to_migrate = [
        (clients_collection, "clients"),
        (projects_collection, "projects"),
        (services_collection, "services"),
        (invoices_collection, "invoices"),
        (payments_collection, "payments"),
        (files_collection, "files"),
    ]
    
    for collection, name in collections_to_migrate:
        add_tenant_id_to_collection(collection, name, default_tenant_id)
    
    # Step 3: Summary
    print("\n" + "=" * 60)
    print("✅ Migration completed successfully!")
    print(f"📊 Default tenant_id: {default_tenant_id}")
    print("\n💡 Next steps:")
    print("   1. Restart your backend server")
    print("   2. All existing data now belongs to 'Default Company'")
    print("   3. Create new companies via /api/companies endpoint")
    print("   4. Invite users to companies via /api/companies/{id}/team/invite")


if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
