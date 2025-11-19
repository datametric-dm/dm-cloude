"""
Script to update all remaining routers with multi-tenancy support
"""
import re

# Files to update
files_to_update = [
    'routers/payments_mongo.py',
    'routers/projects_mongo.py',
    'routers/services_mongo.py',
    'routers/reports_mongo.py',
    'routers/files_mongo.py',
]

def add_tenant_support(file_path):
    """Add tenant_id support to a router file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if already has Header import
    if 'from fastapi import' in content and ', Header' not in content:
        content = re.sub(
            r'from fastapi import (.*?)(\n)',
            r'from fastapi import \1, Header\2',
            content
        )
    
    # Add x_company_id to function signatures that don't have it
    # Pattern: function with Depends(get_db) but no x_company_id
    def add_header_param(match):
        func_def = match.group(0)
        if 'x_company_id' in func_def:
            return func_def  # Already has it
        
        # Add before closing ):
        func_def = func_def.rstrip()
        if func_def.endswith(')'):
            func_def = func_def[:-1]
        func_def += ',\n    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")\n)'
        return func_def
    
    # Find all async def functions with Depends(get_db)
    content = re.sub(
        r'async def .*?\n.*?db = Depends\(get_db\)\n\):',
        add_header_param,
        content,
        flags=re.DOTALL
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {file_path}")

if __name__ == '__main__':
    for file_path in files_to_update:
        try:
            add_tenant_support(file_path)
        except Exception as e:
            print(f"❌ Failed to update {file_path}: {e}")
