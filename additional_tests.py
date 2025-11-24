#!/usr/bin/env python3
"""
Additional specific tests for the review request scenarios
"""

import requests
import json
from datetime import datetime, date, timedelta

BACKEND_URL = "https://agencysuite.preview.emergentagent.com/api"

def test_specific_scenarios():
    """Test the specific scenarios mentioned in the review request"""
    session = requests.Session()
    
    # Login to get user info
    login_data = {
        "email": "adminDM@test.com",
        "password": "adminDM4321!"
    }
    
    login_response = session.post(f"{BACKEND_URL}/login", json=login_data)
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    user_data = login_response.json()
    user_id = user_data.get("user", {}).get("id")
    auth_token = user_data.get("access_token", "dummy-token")
    
    print(f"✅ Logged in as user: {user_id}")
    
    # Get existing companies from MongoDB
    headers = {"X-User-ID": user_id}
    companies_response = session.get(f"{BACKEND_URL}/companies/my", headers=headers)
    
    if companies_response.status_code != 200:
        print("❌ Failed to get companies")
        return False
    
    companies = companies_response.json().get("companies", [])
    if not companies:
        print("❌ No companies found")
        return False
    
    company_id = companies[0]["id"]
    print(f"✅ Using company: {company_id}")
    
    # Get existing clients
    client_headers = {
        "X-User-ID": user_id,
        "X-Company-ID": company_id,
        "Authorization": f"Bearer {auth_token}"
    }
    
    clients_response = session.get(f"{BACKEND_URL}/clients/", headers=client_headers)
    if clients_response.status_code != 200:
        print("❌ Failed to get clients")
        return False
    
    clients = clients_response.json().get("clients", [])
    if not clients:
        print("❌ No clients found")
        return False
    
    client_id = clients[0]["id"]
    print(f"✅ Using client: {client_id}")
    
    # Get existing projects
    projects_response = session.get(f"{BACKEND_URL}/projects/", headers=client_headers)
    if projects_response.status_code != 200:
        print("❌ Failed to get projects")
        return False
    
    projects = projects_response.json().get("projects", [])
    if not projects:
        print("❌ No projects found")
        return False
    
    project_id = projects[0]["id"]
    print(f"✅ Using project: {project_id}")
    
    print("\n🧪 Testing Critical Scenarios from Review Request...")
    
    # Тест 1: Создание и получение счета (Invoices)
    print("\n📋 Тест 1: Создание и получение счета")
    
    today = date.today()
    due_date = today + timedelta(days=30)
    
    invoice_data = {
        "project_id": project_id,
        "client_id": client_id,
        "number": "INV-001",
        "amount": 50000,
        "status": "draft",
        "date_issued": today.isoformat(),
        "date_due": due_date.isoformat()
    }
    
    # 1. POST /api/invoices - создать счет
    invoice_response = session.post(f"{BACKEND_URL}/invoices/", json=invoice_data, headers=client_headers)
    if invoice_response.status_code == 201:
        invoice_id = invoice_response.json().get("id")
        tenant_id = invoice_response.json().get("tenant_id")
        print(f"✅ Invoice created: {invoice_id}, tenant_id: {tenant_id}")
        
        # 2. GET /api/invoices - проверить что счет появился в списке
        invoices_list = session.get(f"{BACKEND_URL}/invoices/", headers=client_headers)
        if invoices_list.status_code == 200:
            invoices = invoices_list.json().get("invoices", [])
            found_invoice = next((inv for inv in invoices if inv.get("id") == invoice_id), None)
            if found_invoice:
                print("✅ Invoice found in list")
            else:
                print("❌ Invoice not found in list")
        
        # 3. GET /api/invoices/{id} - получить конкретный счет
        invoice_detail = session.get(f"{BACKEND_URL}/invoices/{invoice_id}", headers=client_headers)
        if invoice_detail.status_code == 200:
            print("✅ Invoice detail retrieved")
        else:
            print("❌ Failed to get invoice detail")
    else:
        print(f"❌ Failed to create invoice: {invoice_response.status_code}")
        return False
    
    # Тест 2: Создание и получение платежа (Payments)
    print("\n💳 Тест 2: Создание и получение платежа")
    
    expected_date = date.today() + timedelta(days=7)
    
    payment_data = {
        "invoice_id": invoice_id,
        "client_id": client_id,
        "amount": 50000,
        "status": "pending",
        "date_expected": expected_date.isoformat()
    }
    
    # 1. POST /api/payments - создать платеж
    payment_response = session.post(f"{BACKEND_URL}/payments/", json=payment_data, headers=client_headers)
    if payment_response.status_code == 201:
        payment_id = payment_response.json().get("id")
        print(f"✅ Payment created: {payment_id}")
        
        # 2. GET /api/payments - проверить список
        payments_list = session.get(f"{BACKEND_URL}/payments/", headers=client_headers)
        if payments_list.status_code == 200:
            print("✅ Payments list retrieved")
        
        # 3. POST /api/payments/{id}/mark-received - отметить как полученный
        mark_received = session.post(f"{BACKEND_URL}/payments/{payment_id}/mark-received", headers=client_headers)
        if mark_received.status_code == 200:
            print("✅ Payment marked as received")
            
            # Проверить изменение статуса
            payment_detail = session.get(f"{BACKEND_URL}/payments/{payment_id}", headers=client_headers)
            if payment_detail.status_code == 200:
                status = payment_detail.json().get("status")
                if status == "received":
                    print("✅ Payment status correctly updated to 'received'")
                else:
                    print(f"❌ Payment status not updated: {status}")
        else:
            print("❌ Failed to mark payment as received")
    else:
        print(f"❌ Failed to create payment: {payment_response.status_code}")
    
    # Тест 3: Создание и получение проекта (Projects)
    print("\n📋 Тест 3: Создание и получение проекта")
    
    project_data = {
        "name": "Test Multi-Tenancy Project",
        "client_id": client_id,
        "status": "in_progress",
        "budget": 100000
    }
    
    # 1. POST /api/projects - создать проект
    new_project_response = session.post(f"{BACKEND_URL}/projects/", json=project_data, headers=client_headers)
    if new_project_response.status_code == 201:
        new_project_id = new_project_response.json().get("id")
        print(f"✅ New project created: {new_project_id}")
        
        # 2. GET /api/projects - проверить список
        projects_list = session.get(f"{BACKEND_URL}/projects/", headers=client_headers)
        if projects_list.status_code == 200:
            print("✅ Projects list retrieved")
        
        # 3. GET /api/projects/{id} - получить конкретный проект
        project_detail = session.get(f"{BACKEND_URL}/projects/{new_project_id}", headers=client_headers)
        if project_detail.status_code == 200:
            print("✅ Project detail retrieved")
        
        # 4. PUT /api/projects/{id} - обновить проект
        update_data = {"budget": 120000}
        project_update = session.put(f"{BACKEND_URL}/projects/{new_project_id}", json=update_data, headers=client_headers)
        if project_update.status_code == 200:
            print("✅ Project updated successfully")
        else:
            print("❌ Failed to update project")
    else:
        print(f"❌ Failed to create new project: {new_project_response.status_code}")
    
    # Тест 4: Изоляция данных (Tenant Isolation)
    print("\n🔒 Тест 4: Изоляция данных между компаниями")
    
    # Create a second company for isolation testing
    if len(companies) > 1:
        company_2_id = companies[1]["id"]
    else:
        # Create second company
        company_2_data = {
            "name": "Second Test Company",
            "email": "test2@company.com",
            "legal_name": "ООО Второй Тест"
        }
        company_2_response = session.post(f"{BACKEND_URL}/companies", json=company_2_data, headers=headers)
        if company_2_response.status_code == 201:
            company_2_id = company_2_response.json().get("company", {}).get("id")
        else:
            print("❌ Failed to create second company")
            return False
    
    print(f"✅ Using second company: {company_2_id}")
    
    # Try to access invoice with wrong company ID
    wrong_headers = {
        "X-User-ID": user_id,
        "X-Company-ID": company_2_id,
        "Authorization": f"Bearer {auth_token}"
    }
    
    # Test invoice isolation
    invoice_isolation = session.get(f"{BACKEND_URL}/invoices/{invoice_id}", headers=wrong_headers)
    if invoice_isolation.status_code == 404:
        print("✅ Invoice tenant isolation working - 404 with wrong company ID")
    else:
        print(f"❌ Invoice tenant isolation failed - got {invoice_isolation.status_code}")
    
    # Test payment isolation
    payment_isolation = session.get(f"{BACKEND_URL}/payments/{payment_id}", headers=wrong_headers)
    if payment_isolation.status_code == 404:
        print("✅ Payment tenant isolation working - 404 with wrong company ID")
    else:
        print(f"❌ Payment tenant isolation failed - got {payment_isolation.status_code}")
    
    # Test project isolation
    project_isolation = session.get(f"{BACKEND_URL}/projects/{new_project_id}", headers=wrong_headers)
    if project_isolation.status_code == 404:
        print("✅ Project tenant isolation working - 404 with wrong company ID")
    else:
        print(f"❌ Project tenant isolation failed - got {project_isolation.status_code}")
    
    # Тест 5: Отчеты (Reports) - базовая проверка
    print("\n📊 Тест 5: Отчеты - базовая проверка")
    
    # GET /api/reports/dashboard - проверить что возвращает данные
    dashboard_response = session.get(f"{BACKEND_URL}/reports/dashboard", headers=client_headers)
    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json()
        required_fields = ["total_clients", "active_projects", "total_revenue", "pending_invoices"]
        
        if all(field in dashboard_data for field in required_fields):
            print("✅ Dashboard reports working - all required fields present")
            print(f"   Data filtered for company: {company_id}")
        else:
            missing = [f for f in required_fields if f not in dashboard_data]
            print(f"❌ Dashboard missing fields: {missing}")
    else:
        print(f"❌ Dashboard reports failed: {dashboard_response.status_code}")
    
    print("\n🎉 ALL CRITICAL TESTS COMPLETED!")
    return True

if __name__ == "__main__":
    test_specific_scenarios()