"""
Initialize default Kanban columns for companies
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.base import companies_collection, kanban_columns_collection
from datetime import datetime
from uuid import uuid4


def create_default_kanban_columns(company_id: str):
    """Create default Kanban columns for a company"""
    
    default_columns = [
        {
            "name": "Новый",
            "type": "new",
            "color": "#94A3B8",  # Gray
            "order": 0,
            "wip_limit": None
        },
        {
            "name": "В работе",
            "type": "in_work",
            "color": "#3B82F6",  # Blue
            "order": 1,
            "wip_limit": 5
        },
        {
            "name": "Презентация",
            "type": "presentation",
            "color": "#8B5CF6",  # Purple
            "order": 2,
            "wip_limit": 3
        },
        {
            "name": "Контроль",
            "type": "control",
            "color": "#F59E0B",  # Amber
            "order": 3,
            "wip_limit": None
        },
        {
            "name": "Готово",
            "type": "done",
            "color": "#10B981",  # Green
            "order": 4,
            "wip_limit": None
        },
        {
            "name": "Архив",
            "type": "archived",
            "color": "#6B7280",  # Gray
            "order": 5,
            "wip_limit": None
        }
    ]
    
    for column in default_columns:
        # Check if column already exists
        existing = kanban_columns_collection.find_one({
            "tenant_id": company_id,
            "type": column["type"]
        })
        
        if not existing:
            column_doc = {
                "id": uuid4().hex,
                "tenant_id": company_id,
                "is_active": True,
                "created_at": datetime.utcnow(),
                **column
            }
            kanban_columns_collection.insert_one(column_doc)
            print(f"✅ Created column '{column['name']}' for company {company_id}")


def run_migration():
    """Run migration for all active companies"""
    print("🚀 Initializing Kanban columns...")
    print("=" * 60)
    
    companies = list(companies_collection.find({"is_active": True}))
    
    for company in companies:
        company_id = company.get("id")
        company_name = company.get("name", "Unknown")
        print(f"\n📦 Processing company: {company_name} ({company_id})")
        
        create_default_kanban_columns(company_id)
    
    print("\n" + "=" * 60)
    print(f"✅ Kanban columns initialized for {len(companies)} companies!")


if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
