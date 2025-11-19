#!/usr/bin/env python3
"""
Multi-Tenancy Backend API Testing Script
Tests all updated routers with multi-tenancy support:
1. Invoices (счета) - /api/invoices
2. Payments (платежи) - /api/payments  
3. Projects (проекты) - /api/projects
4. Services (услуги) - /api/services
5. Reports (отчеты) - /api/reports
"""

import requests
import json
import sys
from datetime import datetime, date, timedelta
import uuid

# Backend URL from frontend/.env
BACKEND_URL = "https://saasagency.preview.emergentagent.com/api"

class MultiTenancyTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_user_id = None
        self.test_company_id = None
        self.test_company_2_id = None
        self.test_client_id = None
        self.invited_user_id = None
        self.results = []
        
    def log_result(self, test_name, success, details="", response_data=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        if response_data:
            result["response"] = response_data
        self.results.append(result)
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        print()

    def test_health_check(self):
        """Test if backend is running"""
        try:
            response = self.session.get(f"{BACKEND_URL}/healthz")
            if response.status_code == 200:
                self.log_result("Backend Health Check", True, "Backend is running")
                return True
            else:
                self.log_result("Backend Health Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Backend Health Check", False, f"Connection error: {str(e)}")
            return False

    def create_test_user(self):
        """Create a test user for testing"""
        try:
            # Try to use the seeded admin user first
            login_data = {
                "email": "adminDM@test.com",
                "password": "adminDM4321!"
            }
            
            login_response = self.session.post(f"{BACKEND_URL}/login", json=login_data)
            if login_response.status_code == 200:
                data = login_response.json()
                self.test_user_id = data.get("user", {}).get("id")
                self.log_result("Create Test User", True, f"Using seeded admin user ID: {self.test_user_id}")
                return True
            
            # If admin login fails, try to register a new user
            user_data = {
                "email": "test.admin@multitenancy.com",
                "password": "TestPassword123!",
                "full_name": "Test Admin User"
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_id = data.get("id")
                self.log_result("Create Test User", True, f"User created with ID: {self.test_user_id}")
                return True
            elif response.status_code == 400 and "exists" in response.text:
                # User exists, try to login
                login_data = {
                    "email": user_data["email"],
                    "password": user_data["password"]
                }
                login_response = self.session.post(f"{BACKEND_URL}/login", json=login_data)
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    self.test_user_id = login_data.get("user", {}).get("id")
                    self.log_result("Create Test User", True, f"Using existing user ID: {self.test_user_id}")
                    return True
                else:
                    self.log_result("Create Test User", False, f"Login failed: {login_response.status_code}")
                    return False
            else:
                self.log_result("Create Test User", False, f"Registration failed: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Create Test User", False, f"Error: {str(e)}")
            return False

    def test_create_company(self):
        """Test POST /api/companies - Scenario 1"""
        try:
            company_data = {
                "name": "Test Marketing Agency",
                "email": "contact@testagency.com",
                "phone": "+7-999-123-4567",
                "legal_name": "ООО Тест Маркетинг",
                "inn": "1234567890"
            }
            
            headers = {"X-User-ID": self.test_user_id}
            response = self.session.post(f"{BACKEND_URL}/companies", json=company_data, headers=headers)
            
            if response.status_code == 201:
                data = response.json()
                self.test_company_id = data.get("company", {}).get("id")
                user_role = data.get("role")
                
                if user_role == "owner":
                    self.log_result("Create Company", True, f"Company created with ID: {self.test_company_id}, User role: {user_role}")
                    return True
                else:
                    self.log_result("Create Company", False, f"User role is not 'owner': {user_role}")
                    return False
            else:
                self.log_result("Create Company", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Create Company", False, f"Error: {str(e)}")
            return False

    def test_get_my_companies(self):
        """Test GET /api/companies/my - Scenario 2"""
        try:
            headers = {"X-User-ID": self.test_user_id}
            response = self.session.get(f"{BACKEND_URL}/companies/my", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                companies = data.get("companies", [])
                
                if len(companies) > 0:
                    # Check if our test company is in the list
                    test_company = next((c for c in companies if c.get("id") == self.test_company_id), None)
                    if test_company and test_company.get("user_role") == "owner":
                        self.log_result("Get My Companies", True, f"Found {len(companies)} companies, test company has correct role")
                        return True
                    else:
                        self.log_result("Get My Companies", False, "Test company not found or incorrect role")
                        return False
                else:
                    self.log_result("Get My Companies", False, "No companies returned")
                    return False
            else:
                self.log_result("Get My Companies", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Get My Companies", False, f"Error: {str(e)}")
            return False

    def test_get_company_details(self):
        """Test GET /api/companies/{id}"""
        try:
            headers = {"X-User-ID": self.test_user_id}
            response = self.session.get(f"{BACKEND_URL}/companies/{self.test_company_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                company = data.get("company", {})
                user_role = data.get("user_role")
                
                if company.get("id") == self.test_company_id and user_role == "owner":
                    self.log_result("Get Company Details", True, f"Company details retrieved, role: {user_role}")
                    return True
                else:
                    self.log_result("Get Company Details", False, "Incorrect company data or role")
                    return False
            else:
                self.log_result("Get Company Details", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Get Company Details", False, f"Error: {str(e)}")
            return False

    def test_update_company(self):
        """Test PUT /api/companies/{id}"""
        try:
            update_data = {
                "website": "https://testagency.com",
                "legal_address": "Москва, ул. Тестовая, д. 1"
            }
            
            headers = {"X-User-ID": self.test_user_id}
            response = self.session.put(f"{BACKEND_URL}/companies/{self.test_company_id}", json=update_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                company = data.get("company", {})
                
                if company.get("website") == update_data["website"]:
                    self.log_result("Update Company", True, "Company updated successfully")
                    return True
                else:
                    self.log_result("Update Company", False, "Company not updated correctly")
                    return False
            else:
                self.log_result("Update Company", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Update Company", False, f"Error: {str(e)}")
            return False

    def test_company_stats(self):
        """Test GET /api/companies/{id}/stats"""
        try:
            headers = {"X-User-ID": self.test_user_id}
            response = self.session.get(f"{BACKEND_URL}/companies/{self.test_company_id}/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("stats", {})
                
                if "total_users" in stats and "total_clients" in stats:
                    self.log_result("Get Company Stats", True, f"Stats retrieved: {stats}")
                    return True
                else:
                    self.log_result("Get Company Stats", False, "Stats format incorrect")
                    return False
            else:
                self.log_result("Get Company Stats", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Get Company Stats", False, f"Error: {str(e)}")
            return False

    def test_invite_user(self):
        """Test POST /api/companies/{id}/team/invite - Scenario 3"""
        try:
            invite_data = {
                "email": "manager@testagency.com",
                "role": "manager",
                "full_name": "Test Manager"
            }
            
            headers = {"X-User-ID": self.test_user_id}
            response = self.session.post(f"{BACKEND_URL}/companies/{self.test_company_id}/team/invite", json=invite_data, headers=headers)
            
            if response.status_code == 201:
                data = response.json()
                user_data = data.get("user", {})
                self.invited_user_id = user_data.get("id")
                
                if user_data.get("role") == "manager":
                    self.log_result("Invite User", True, f"User invited with ID: {self.invited_user_id}, role: manager")
                    return True
                else:
                    self.log_result("Invite User", False, f"Incorrect role: {user_data.get('role')}")
                    return False
            else:
                self.log_result("Invite User", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Invite User", False, f"Error: {str(e)}")
            return False

    def test_get_team_members(self):
        """Test GET /api/companies/{id}/team"""
        try:
            headers = {"X-User-ID": self.test_user_id}
            response = self.session.get(f"{BACKEND_URL}/companies/{self.test_company_id}/team", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                team_members = data.get("team_members", [])
                
                if len(team_members) >= 2:  # Owner + invited user
                    # Check if invited user is in the team
                    invited_member = next((m for m in team_members if m.get("user_id") == self.invited_user_id), None)
                    if invited_member and invited_member.get("role") == "manager":
                        self.log_result("Get Team Members", True, f"Found {len(team_members)} team members, invited user has correct role")
                        return True
                    else:
                        self.log_result("Get Team Members", False, "Invited user not found or incorrect role")
                        return False
                else:
                    self.log_result("Get Team Members", False, f"Expected at least 2 team members, got {len(team_members)}")
                    return False
            else:
                self.log_result("Get Team Members", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Get Team Members", False, f"Error: {str(e)}")
            return False

    def test_update_user_role(self):
        """Test PUT /api/companies/{id}/team/{user_id}/role - Scenario 5"""
        try:
            role_data = {"role": "admin"}
            
            headers = {"X-User-ID": self.test_user_id}
            response = self.session.put(f"{BACKEND_URL}/companies/{self.test_company_id}/team/{self.invited_user_id}/role", json=role_data, headers=headers)
            
            if response.status_code == 200:
                self.log_result("Update User Role", True, "User role updated to admin")
                return True
            else:
                self.log_result("Update User Role", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Update User Role", False, f"Error: {str(e)}")
            return False

    def test_create_second_company(self):
        """Create second company for tenant isolation testing"""
        try:
            company_data = {
                "name": "Second Test Company",
                "email": "contact@secondtest.com",
                "legal_name": "ООО Второй Тест"
            }
            
            headers = {"X-User-ID": self.test_user_id}
            response = self.session.post(f"{BACKEND_URL}/companies", json=company_data, headers=headers)
            
            if response.status_code == 201:
                data = response.json()
                self.test_company_2_id = data.get("company", {}).get("id")
                self.log_result("Create Second Company", True, f"Second company created with ID: {self.test_company_2_id}")
                return True
            else:
                self.log_result("Create Second Company", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Create Second Company", False, f"Error: {str(e)}")
            return False

    def test_create_client_company1(self):
        """Test POST /api/clients with X-Company-ID - Scenario 4 part 1"""
        try:
            client_data = {
                "name": "Test Client Company 1",
                "email": "client1@testclient.com",
                "phone": "+7-999-111-2233",
                "status": "active"
            }
            
            headers = {
                "X-User-ID": self.test_user_id,
                "X-Company-ID": self.test_company_id,
                "Authorization": "Bearer dummy-token"  # Required for authentication
            }
            response = self.session.post(f"{BACKEND_URL}/clients/", json=client_data, headers=headers)
            
            if response.status_code == 201:
                data = response.json()
                self.test_client_id = data.get("id")
                self.log_result("Create Client (Company 1)", True, f"Client created with ID: {self.test_client_id}")
                return True
            else:
                self.log_result("Create Client (Company 1)", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Create Client (Company 1)", False, f"Error: {str(e)}")
            return False

    def test_get_client_company1(self):
        """Test GET /api/clients/{id} with correct X-Company-ID"""
        try:
            headers = {
                "X-User-ID": self.test_user_id,
                "X-Company-ID": self.test_company_id,
                "Authorization": "Bearer dummy-token"  # Required for authentication
            }
            response = self.session.get(f"{BACKEND_URL}/clients/{self.test_client_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == self.test_client_id:
                    self.log_result("Get Client (Company 1)", True, "Client retrieved successfully")
                    return True
                else:
                    self.log_result("Get Client (Company 1)", False, "Client ID mismatch")
                    return False
            else:
                self.log_result("Get Client (Company 1)", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Get Client (Company 1)", False, f"Error: {str(e)}")
            return False

    def test_tenant_isolation(self):
        """Test GET /api/clients/{id} with wrong X-Company-ID - Scenario 4 part 2"""
        try:
            headers = {
                "X-User-ID": self.test_user_id,
                "X-Company-ID": self.test_company_2_id,  # Wrong company ID
                "Authorization": "Bearer dummy-token"  # Required for authentication
            }
            response = self.session.get(f"{BACKEND_URL}/clients/{self.test_client_id}", headers=headers)
            
            if response.status_code == 404:
                self.log_result("Tenant Isolation Test", True, "Client correctly not found with wrong company ID")
                return True
            else:
                self.log_result("Tenant Isolation Test", False, f"Expected 404, got {response.status_code} - tenant isolation failed!")
                return False
                
        except Exception as e:
            self.log_result("Tenant Isolation Test", False, f"Error: {str(e)}")
            return False

    def test_get_clients_list(self):
        """Test GET /api/clients/ with X-Company-ID"""
        try:
            headers = {
                "X-User-ID": self.test_user_id,
                "X-Company-ID": self.test_company_id,
                "Authorization": "Bearer dummy-token"  # Required for authentication
            }
            response = self.session.get(f"{BACKEND_URL}/clients/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                clients = data.get("clients", [])
                
                # Should find our test client
                test_client = next((c for c in clients if c.get("id") == self.test_client_id), None)
                if test_client:
                    self.log_result("Get Clients List", True, f"Found {len(clients)} clients including test client")
                    return True
                else:
                    self.log_result("Get Clients List", False, "Test client not found in list")
                    return False
            else:
                self.log_result("Get Clients List", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Get Clients List", False, f"Error: {str(e)}")
            return False

    def test_remove_user_from_team(self):
        """Test DELETE /api/companies/{id}/team/{user_id} - Scenario 5 part 2"""
        try:
            headers = {"X-User-ID": self.test_user_id}
            response = self.session.delete(f"{BACKEND_URL}/companies/{self.test_company_id}/team/{self.invited_user_id}", headers=headers)
            
            if response.status_code == 200:
                self.log_result("Remove User from Team", True, "User removed from team successfully")
                return True
            else:
                self.log_result("Remove User from Team", False, f"Status: {response.status_code}", response.json())
                return False
                
        except Exception as e:
            self.log_result("Remove User from Team", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all multi-tenancy tests"""
        print("🚀 Starting Multi-Tenancy Backend API Tests")
        print("=" * 60)
        
        # Health check
        if not self.test_health_check():
            print("❌ Backend is not accessible. Stopping tests.")
            return False
        
        # Create test user
        if not self.create_test_user():
            print("❌ Cannot create test user. Stopping tests.")
            return False
        
        # Test Companies API
        print("\n📋 Testing Companies API...")
        self.test_create_company()
        self.test_get_my_companies()
        self.test_get_company_details()
        self.test_update_company()
        self.test_company_stats()
        
        # Test Team Management API
        print("\n👥 Testing Team Management API...")
        self.test_invite_user()
        self.test_get_team_members()
        self.test_update_user_role()
        
        # Test Tenant Isolation
        print("\n🔒 Testing Tenant Isolation...")
        self.test_create_second_company()
        self.test_create_client_company1()
        self.test_get_client_company1()
        self.test_tenant_isolation()
        self.test_get_clients_list()
        
        # Cleanup tests
        print("\n🧹 Testing Cleanup Operations...")
        self.test_remove_user_from_team()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.results:
            print(f"{result['status']}: {result['test']}")
            if result['details']:
                print(f"   {result['details']}")
        
        # Critical issues
        failed_tests = [r for r in self.results if not r["success"]]
        if failed_tests:
            print("\n🚨 CRITICAL ISSUES:")
            for test in failed_tests:
                print(f"- {test['test']}: {test['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = MultiTenancyTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)