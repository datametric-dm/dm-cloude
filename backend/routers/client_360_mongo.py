"""
Client 360 API - comprehensive client view
"""
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import uuid4

from database.base import (
    clients_collection,
    client_interactions_collection,
    client_health_scores_collection,
    client_timelines_collection,
    projects_collection,
    invoices_collection,
    payments_collection
)
from routers.auth_mongo import get_current_user

router = APIRouter(tags=["client-360"], prefix="/client-360")


# ============= Client Profile =============

@router.get("/clients/{client_id}/profile")
async def get_client_360_profile(
    client_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get complete Client 360 profile"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Get client
    client = clients_collection.find_one({
        "id": client_id,
        "tenant_id": x_company_id
    })
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client.pop("_id", None)
    
    # Get projects
    projects = list(projects_collection.find({
        "client_id": client_id,
        "tenant_id": x_company_id
    }))
    
    total_projects = len(projects)
    active_projects = len([p for p in projects if p.get("status") in ["in_progress", "planning"]])
    completed_projects = len([p for p in projects if p.get("status") == "completed"])
    
    # Get invoices
    invoices = list(invoices_collection.find({
        "client_id": client_id,
        "tenant_id": x_company_id
    }))
    
    total_revenue = sum(inv.get("amount", 0) for inv in invoices)
    
    # Get payments
    payments = list(payments_collection.find({
        "client_id": client_id,
        "tenant_id": x_company_id
    }))
    
    total_paid = sum(pay.get("amount", 0) for pay in payments if pay.get("status") == "received")
    
    overdue_invoices = [inv for inv in invoices if inv.get("status") == "overdue"]
    total_overdue = sum(inv.get("amount", 0) for inv in overdue_invoices)
    
    # Get interactions
    interactions = list(client_interactions_collection.find({
        "client_id": client_id,
        "tenant_id": x_company_id
    }).sort("interaction_date", -1).limit(10))
    
    for interaction in interactions:
        interaction.pop("_id", None)
    
    # Get timeline
    timeline = list(client_timelines_collection.find({
        "client_id": client_id,
        "tenant_id": x_company_id
    }).sort("event_date", -1).limit(20))
    
    for event in timeline:
        event.pop("_id", None)
    
    # Calculate dates
    first_project_date = min([p.get("created_at") for p in projects if p.get("created_at")], default=None)
    last_project_date = max([p.get("created_at") for p in projects if p.get("created_at")], default=None)
    last_payment_date = max([pay.get("date_received") for pay in payments if pay.get("date_received")], default=None)
    last_interaction_date = max([int.get("interaction_date") for int in interactions if int.get("interaction_date")], default=None)
    
    days_since_last_interaction = 0
    if last_interaction_date:
        days_since_last_interaction = (datetime.utcnow() - last_interaction_date).days
    
    # Get health score
    health_score = client_health_scores_collection.find_one({
        "client_id": client_id,
        "tenant_id": x_company_id
    })
    
    if health_score:
        health_score.pop("_id", None)
    
    # Build profile
    profile = {
        "client_id": client_id,
        "tenant_id": x_company_id,
        "client_name": client.get("name"),
        "email": client.get("email"),
        "phone": client.get("phone"),
        "health_score": health_score,
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "total_revenue": total_revenue,
        "total_paid": total_paid,
        "total_overdue": total_overdue,
        "first_project_date": first_project_date.isoformat() if first_project_date else None,
        "last_project_date": last_project_date.isoformat() if last_project_date else None,
        "last_payment_date": last_payment_date.isoformat() if last_payment_date else None,
        "last_interaction_date": last_interaction_date.isoformat() if last_interaction_date else None,
        "days_since_last_interaction": days_since_last_interaction,
        "interaction_count": len(interactions),
        "timeline": timeline,
        "recent_interactions": interactions,
        "tags": health_score.get("tags", []) if health_score else []
    }
    
    return {"profile": profile}


# ============= Interactions =============

class InteractionCreate(BaseModel):
    client_id: str
    type: str
    title: str
    description: Optional[str] = None
    contact_person: Optional[str] = None
    project_id: Optional[str] = None
    interaction_date: Optional[datetime] = None


@router.post("/interactions")
async def create_interaction(
    interaction_data: InteractionCreate,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """Create client interaction"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    interaction_dict = interaction_data.dict()
    interaction_dict.update({
        "id": uuid4().hex,
        "tenant_id": x_company_id,
        "user_id": x_user_id,
        "source": "manual",
        "created_at": datetime.utcnow(),
        "created_by": x_user_id
    })
    
    if not interaction_dict.get("interaction_date"):
        interaction_dict["interaction_date"] = datetime.utcnow()
    
    client_interactions_collection.insert_one(interaction_dict)
    interaction_dict.pop("_id", None)
    
    # Add to timeline
    timeline_event = {
        "id": uuid4().hex,
        "tenant_id": x_company_id,
        "client_id": interaction_data.client_id,
        "event_type": "interaction",
        "event_title": interaction_data.title,
        "event_description": interaction_data.description,
        "event_date": interaction_dict["interaction_date"],
        "created_at": datetime.utcnow()
    }
    client_timelines_collection.insert_one(timeline_event)
    
    return {"message": "Interaction created", "interaction": interaction_dict}


@router.get("/clients/{client_id}/interactions")
async def get_client_interactions(
    client_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get client interactions"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    interactions = list(client_interactions_collection.find({
        "client_id": client_id,
        "tenant_id": x_company_id
    }).sort("interaction_date", -1))
    
    for interaction in interactions:
        interaction.pop("_id", None)
    
    return {"interactions": interactions, "count": len(interactions)}


# ============= Health Score =============

@router.post("/clients/{client_id}/calculate-health")
async def calculate_client_health(
    client_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Calculate client health score"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Get client data
    client = clients_collection.find_one({
        "id": client_id,
        "tenant_id": x_company_id
    })
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get invoices and payments
    invoices = list(invoices_collection.find({
        "client_id": client_id,
        "tenant_id": x_company_id
    }))
    
    payments = list(payments_collection.find({
        "client_id": client_id,
        "tenant_id": x_company_id,
        "status": "received"
    }))
    
    # Payment score (0-100)
    overdue_count = len([inv for inv in invoices if inv.get("status") == "overdue"])
    total_invoices = len(invoices)
    
    if total_invoices > 0:
        on_time_rate = (total_invoices - overdue_count) / total_invoices
        payment_score = on_time_rate * 100
    else:
        payment_score = 100
    
    # Calculate avg payment delay
    payment_delays = []
    for payment in payments:
        if payment.get("date_received") and payment.get("date_expected"):
            delay = (payment["date_received"] - payment["date_expected"]).days
            payment_delays.append(max(0, delay))
    
    avg_payment_delay = sum(payment_delays) / len(payment_delays) if payment_delays else 0
    
    # Project score
    projects = list(projects_collection.find({
        "client_id": client_id,
        "tenant_id": x_company_id
    }))
    
    completed_projects = len([p for p in projects if p.get("status") == "completed"])
    total_projects = len(projects)
    
    if total_projects > 0:
        project_score = (completed_projects / total_projects) * 100
    else:
        project_score = 50
    
    # Communication score
    interactions = list(client_interactions_collection.find({
        "client_id": client_id,
        "tenant_id": x_company_id
    }))
    
    if interactions:
        last_interaction = max(interactions, key=lambda x: x.get("interaction_date", datetime.min))
        days_since = (datetime.utcnow() - last_interaction.get("interaction_date", datetime.utcnow())).days
        
        if days_since < 7:
            communication_score = 100
        elif days_since < 14:
            communication_score = 80
        elif days_since < 30:
            communication_score = 60
        else:
            communication_score = 30
    else:
        communication_score = 50
    
    # Engagement score
    recent_interactions = len([i for i in interactions if (datetime.utcnow() - i.get("interaction_date", datetime.min)).days < 30])
    engagement_score = min(100, recent_interactions * 20)
    
    # Overall score
    overall_score = (
        payment_score * 0.3 +
        project_score * 0.25 +
        communication_score * 0.25 +
        engagement_score * 0.2
    )
    
    # Determine status
    if overall_score >= 80:
        status = "excellent"
    elif overall_score >= 60:
        status = "good"
    elif overall_score >= 40:
        status = "fair"
    elif overall_score >= 20:
        status = "poor"
    else:
        status = "critical"
    
    # Calculate churn probability
    churn_factors = []
    if overdue_count > 0:
        churn_factors.append(0.3)
    if avg_payment_delay > 7:
        churn_factors.append(0.2)
    if days_since > 30:
        churn_factors.append(0.4)
    if overall_score < 40:
        churn_factors.append(0.3)
    
    churn_probability = min(1.0, sum(churn_factors))
    
    # Determine tags
    tags = []
    if overall_score >= 80:
        tags.append("vip")
    if churn_probability > 0.5:
        tags.append("churn_risk")
    if overdue_count > 2:
        tags.append("risk")
    if total_projects > 5:
        tags.append("loyal")
    
    # Recommendations
    recommendations = []
    if churn_probability > 0.5:
        recommendations.append("High churn risk - schedule check-in call")
    if overdue_count > 0:
        recommendations.append(f"Follow up on {overdue_count} overdue invoices")
    if days_since > 30:
        recommendations.append("No recent interactions - reach out to client")
    
    # Save health score
    health_score = {
        "id": uuid4().hex,
        "tenant_id": x_company_id,
        "client_id": client_id,
        "score": overall_score,
        "status": status,
        "payment_score": payment_score,
        "project_score": project_score,
        "communication_score": communication_score,
        "engagement_score": engagement_score,
        "satisfaction_score": 0,  # TODO: implement NPS
        "total_revenue": sum(inv.get("amount", 0) for inv in invoices),
        "avg_payment_delay": avg_payment_delay,
        "overdue_count": overdue_count,
        "completed_projects": completed_projects,
        "active_projects": len([p for p in projects if p.get("status") in ["in_progress", "planning"]]),
        "last_interaction_days": days_since if interactions else 999,
        "tags": tags,
        "churn_probability": churn_probability,
        "risk_level": "high" if churn_probability > 0.6 else "medium" if churn_probability > 0.3 else "low",
        "recommendations": recommendations,
        "calculated_at": datetime.utcnow()
    }
    
    # Update or insert
    client_health_scores_collection.update_one(
        {"client_id": client_id, "tenant_id": x_company_id},
        {"$set": health_score},
        upsert=True
    )
    
    return {"message": "Health score calculated", "health_score": health_score}


# ============= Timeline =============

@router.get("/clients/{client_id}/timeline")
async def get_client_timeline(
    client_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get client timeline"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    timeline = list(client_timelines_collection.find({
        "client_id": client_id,
        "tenant_id": x_company_id
    }).sort("event_date", -1))
    
    for event in timeline:
        event.pop("_id", None)
    
    return {"timeline": timeline, "count": len(timeline)}


# ============= Tags Management =============

@router.post("/clients/{client_id}/tags")
async def add_client_tag(
    client_id: str,
    tag: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Add tag to client"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    result = client_health_scores_collection.update_one(
        {"client_id": client_id, "tenant_id": x_company_id},
        {"$addToSet": {"tags": tag}}
    )
    
    return {"message": f"Tag '{tag}' added to client"}


@router.delete("/clients/{client_id}/tags/{tag}")
async def remove_client_tag(
    client_id: str,
    tag: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Remove tag from client"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    result = client_health_scores_collection.update_one(
        {"client_id": client_id, "tenant_id": x_company_id},
        {"$pull": {"tags": tag}}
    )
    
    return {"message": f"Tag '{tag}' removed from client"}
