"""
sCloud.ru Accounting Integration Service
Based on sCloud API integration playbook
"""
import httpx
import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class SCloudAPIClient:
    """Async client for sCloud API communication with OAuth 2.0 support."""
    
    def __init__(self):
        self.client_id = os.getenv("SCLOUD_CLIENT_ID", "")
        self.client_secret = os.getenv("SCLOUD_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("SCLOUD_REDIRECT_URI", "")
        self.base_url = os.getenv("SCLOUD_API_BASE_URL", "https://scloud.live")
        self.scopes = "user.account user.profile user.finances"
        
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.timeout = 30
    
    async def get_authorization_url(self, state: str) -> str:
        """Generate OAuth 2.0 authorization URL for user consent."""
        auth_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": self.scopes,
            "state": state
        }
        
        auth_url = f"{self.base_url}/OAuth2/authorize?"
        auth_url += "&".join([f"{k}={v}" for k, v in auth_params.items()])
        
        logger.info(f"Generated authorization URL for state: {state}")
        return auth_url
    
    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens."""
        token_url = f"{self.base_url}/OAuth2/access_token"
        
        payload = {
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(token_url, data=payload)
                response.raise_for_status()
                
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                
                # Calculate token expiry time with 5-minute buffer
                expires_in = token_data.get("expires_in", 3600)
                self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 300)
                
                logger.info("Successfully exchanged authorization code for tokens")
                return token_data
                
        except httpx.HTTPError as e:
            logger.error(f"Token exchange failed: {str(e)}")
            raise
    
    async def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh access token using the refresh token."""
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        token_url = f"{self.base_url}/OAuth2/access_token"
        
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(token_url, data=payload)
                response.raise_for_status()
                
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                
                # Update refresh token if a new one was provided
                if "refresh_token" in token_data:
                    self.refresh_token = token_data.get("refresh_token")
                
                # Calculate new expiry time
                expires_in = token_data.get("expires_in", 3600)
                self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in - 300)
                
                logger.info("Successfully refreshed access token")
                return token_data
                
        except httpx.HTTPError as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise
    
    async def ensure_valid_token(self) -> None:
        """Ensure access token is valid, refreshing if necessary."""
        if not self.access_token:
            raise ValueError("No access token available. Complete OAuth flow first.")
        
        if self.token_expiry and datetime.utcnow() >= self.token_expiry:
            await self.refresh_access_token()
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Retrieve authenticated user information."""
        await self.ensure_valid_token()
        
        url = f"{self.base_url}/api/v1/user/info"
        headers = self._get_auth_headers()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to retrieve user info: {str(e)}")
            raise
    
    async def get_financial_data(
        self, 
        data_type: str, 
        filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Retrieve financial data from sCloud.
        
        Args:
            data_type: Type of financial data (invoices, transactions, etc.)
            filters: Optional filters for the query
            
        Returns:
            Financial data from sCloud
        """
        await self.ensure_valid_token()
        
        url = f"{self.base_url}/api/v1/financial/{data_type}"
        headers = self._get_auth_headers()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url, 
                    headers=headers, 
                    params=filters or {}
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to retrieve {data_type} data: {str(e)}")
            raise
    
    async def sync_invoices(self, company_id: str, since_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Sync invoices from sCloud for a specific company.
        
        Args:
            company_id: Company identifier
            since_date: Optional date to sync from
            
        Returns:
            Synced invoice data
        """
        filters = {}
        if since_date:
            filters["since"] = since_date.isoformat()
        
        try:
            invoices_data = await self.get_financial_data("invoices", filters)
            logger.info(f"Successfully synced {len(invoices_data.get('items', []))} invoices for company {company_id}")
            return invoices_data
        except Exception as e:
            logger.error(f"Failed to sync invoices for company {company_id}: {str(e)}")
            raise
    
    async def sync_transactions(
        self, 
        company_id: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Sync financial transactions from sCloud.
        
        Args:
            company_id: Company identifier
            start_date: Start date for transaction range
            end_date: End date for transaction range
            
        Returns:
            Synced transaction data
        """
        filters = {}
        if start_date:
            filters["start_date"] = start_date.isoformat()
        if end_date:
            filters["end_date"] = end_date.isoformat()
        
        try:
            transactions_data = await self.get_financial_data("transactions", filters)
            logger.info(f"Successfully synced {len(transactions_data.get('items', []))} transactions for company {company_id}")
            return transactions_data
        except Exception as e:
            logger.error(f"Failed to sync transactions for company {company_id}: {str(e)}")
            raise
