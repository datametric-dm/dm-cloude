"""
Risk Analyzer API - AI-powered risk detection
"""
from fastapi import APIRouter, HTTPException, Header, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import uuid4

from database.base import (
    risks_collection,
    project_risk_analyses_collection,
    team_risk_analyses_collection,
    client_churn_risks_collection,
    projects_collection,
    project_stages_collection,
    invoices_collection,
    payments_collection,
    work_time_records_collection,
    client_interactions_collection,
    user_company_roles_collection
)
from routers.auth_mongo import get_current_user

router = APIRouter(tags=["risk-analyzer"], prefix="/risk-analyzer")


# ============= Risk Detection =============

@router.post("/analyze/project/{project_id}")
async def analyze_project_risks(
    project_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Analyze project risks"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    project = projects_collection.find_one({"id": project_id, "tenant_id": x_company_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    detected_risks = []
    
    # 1. Check for inactive project (stuck)
    stages = list(project_stages_collection.find({"project_id": project_id, "tenant_id": x_company_id}))
    
    for stage in stages:
        last_activity = stage.get("last_activity_at", stage.get("created_at", datetime.utcnow()))
        days_inactive = (datetime.utcnow() - last_activity).days
        
        if days_inactive > 7 and stage.get("status") in ["not_started", "in_progress"]:
            risk = {
                "id": uuid4().hex,
                "tenant_id": x_company_id,
                "category": "project_delay",
                "level": "high" if days_inactive > 14 else "medium",
                "status": "detected",
                "title": f"Stage inactive for {days_inactive} days",
                "description": f"Stage '{stage.get('name')}' has no activity for {days_inactive} days",
                "impact": "Project timeline at risk",
                "project_id": project_id,
                "stage_id": stage.get("id"),
                "probability": min(1.0, days_inactive / 30),
                "severity_score": min(100, days_inactive * 5),
                "confidence": 0.9,
                "indicators": [f"{days_inactive} days without updates"],
                "recommendations": [
                    "Contact project manager for status update",
                    "Review stage requirements and blockers",
                    "Consider reassigning resources"
                ],
                "detected_at": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            detected_risks.append(risk)
            risks_collection.insert_one(risk)
    
    # 2. Check for overdue deadlines
    for stage in stages:
        deadline = stage.get("deadline")
        if deadline and deadline < datetime.utcnow() and stage.get("status") != "completed":
            days_overdue = (datetime.utcnow() - deadline).days
            risk = {
                "id": uuid4().hex,
                "tenant_id": x_company_id,
                "category": "project_delay",
                "level": "critical" if days_overdue > 7 else "high",
                "status": "detected",
                "title": f"Deadline overdue by {days_overdue} days",
                "description": f"Stage '{stage.get('name')}' is {days_overdue} days past deadline",
                "impact": "Client expectations not met, potential penalties",
                "project_id": project_id,
                "stage_id": stage.get("id"),
                "probability": 1.0,
                "severity_score": min(100, days_overdue * 10),
                "confidence": 1.0,
                "indicators": [f"Deadline: {deadline.isoformat()}, Today: {datetime.utcnow().isoformat()}"],
                "recommendations": [
                    "Immediate escalation required",
                    "Communicate with client about delay",
                    "Review timeline and adjust expectations"
                ],
                "detected_at": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            detected_risks.append(risk)
            risks_collection.insert_one(risk)
    
    # 3. Check for low velocity
    completed_stages = [s for s in stages if s.get("status") == "completed"]
    if len(stages) > 0 and len(completed_stages) / len(stages) < 0.3:
        risk = {
            "id": uuid4().hex,
            "tenant_id": x_company_id,
            "category": "low_velocity",
            "level": "medium",
            "status": "detected",
            "title": "Low project completion rate",
            "description": f"Only {len(completed_stages)}/{len(stages)} stages completed",
            "impact": "Project may miss final deadline",
            "project_id": project_id,
            "probability": 0.7,
            "severity_score": 60,
            "confidence": 0.8,
            "indicators": [f"Completion rate: {len(completed_stages)/len(stages)*100:.1f}%"],
            "recommendations": [
                "Review resource allocation",
                "Identify and remove blockers",
                "Consider additional team members"
            ],
            "detected_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        detected_risks.append(risk)
        risks_collection.insert_one(risk)
    
    # Calculate overall risk
    if detected_risks:
        avg_severity = sum(r["severity_score"] for r in detected_risks) / len(detected_risks)
        if avg_severity > 75:
            overall_level = "critical"
        elif avg_severity > 50:
            overall_level = "high"
        elif avg_severity > 25:
            overall_level = "medium"
        else:
            overall_level = "low"
    else:
        overall_level = "low"
        avg_severity = 0
    
    analysis = {
        "id": uuid4().hex,
        "tenant_id": x_company_id,
        "project_id": project_id,
        "overall_risk_level": overall_level,
        "overall_risk_score": avg_severity,
        "active_risks": detected_risks,
        "risk_count": len(detected_risks),
        "analyzed_at": datetime.utcnow()
    }
    
    project_risk_analyses_collection.update_one(
        {"project_id": project_id, "tenant_id": x_company_id},
        {"$set": analysis},
        upsert=True
    )
    
    return {"message": f"Detected {len(detected_risks)} risks", "analysis": analysis}


@router.post("/analyze/client/{client_id}/churn")
async def analyze_client_churn_risk(
    client_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Analyze client churn risk"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Get interactions
    interactions = list(client_interactions_collection.find({
        "client_id": client_id,
        "tenant_id": x_company_id
    }).sort("interaction_date", -1))
    
    days_since_last = 999
    if interactions:
        last_interaction = interactions[0].get("interaction_date", datetime.utcnow())
        days_since_last = (datetime.utcnow() - last_interaction).days
    
    # Get overdue payments
    overdue_invoices = list(invoices_collection.find({
        "client_id": client_id,
        "tenant_id": x_company_id,
        "status": "overdue"
    }))
    
    overdue_count = len(overdue_invoices)
    overdue_amount = sum(inv.get("amount", 0) for inv in overdue_invoices)
    
    # Calculate churn probability
    churn_score = 0.0
    
    if days_since_last > 60:
        churn_score += 0.4
    elif days_since_last > 30:
        churn_score += 0.2
    
    if overdue_count > 2:
        churn_score += 0.3
    elif overdue_count > 0:
        churn_score += 0.15
    
    if overdue_amount > 100000:
        churn_score += 0.3
    elif overdue_amount > 50000:
        churn_score += 0.15
    
    churn_probability = min(1.0, churn_score)
    
    if churn_probability > 0.7:
        risk_level = "critical"
    elif churn_probability > 0.5:
        risk_level = "high"
    elif churn_probability > 0.3:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    # Recommendations
    recommendations = []
    if days_since_last > 30:
        recommendations.append("Schedule immediate check-in call")
    if overdue_count > 0:
        recommendations.append(f"Urgent: Follow up on {overdue_count} overdue invoices")
    if churn_probability > 0.5:
        recommendations.append("Escalate to account manager - high churn risk")
    
    analysis = {
        "id": uuid4().hex,
        "tenant_id": x_company_id,
        "client_id": client_id,
        "churn_probability": churn_probability,
        "risk_level": risk_level,
        "days_since_last_interaction": days_since_last,
        "overdue_payments_count": overdue_count,
        "overdue_amount": overdue_amount,
        "retention_actions": recommendations,
        "analyzed_at": datetime.utcnow()
    }
    
    client_churn_risks_collection.update_one(
        {"client_id": client_id, "tenant_id": x_company_id},
        {"$set": analysis},
        upsert=True
    )
    
    # Create risk if high
    if churn_probability > 0.5:
        risk = {
            "id": uuid4().hex,
            "tenant_id": x_company_id,
            "category": "client_churn",
            "level": risk_level,
            "status": "detected",
            "title": f"High churn risk for client ({churn_probability*100:.0f}%)",
            "description": f"Client shows signs of disengagement",
            "impact": "Potential revenue loss",
            "client_id": client_id,
            "probability": churn_probability,
            "severity_score": churn_probability * 100,
            "confidence": 0.85,
            "indicators": [
                f"{days_since_last} days since last interaction",
                f"{overdue_count} overdue invoices",
                f"{overdue_amount} RUB overdue"
            ],
            "recommendations": recommendations,
            "detected_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        risks_collection.insert_one(risk)
    
    return {"message": "Churn analysis complete", "analysis": analysis}


@router.post("/analyze/team/{user_id}")
async def analyze_team_member_risks(
    user_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Analyze team member workload risks"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Get workload
    now = datetime.utcnow()
    week_start = now - timedelta(days=7)
    
    time_records = list(work_time_records_collection.find({
        "tenant_id": x_company_id,
        "user_id": user_id,
        "date": {"$gte": week_start, "$lte": now}
    }))
    
    total_hours = sum(rec.get("hours", 0) for rec in time_records)
    load_percentage = (total_hours / 40 * 100)
    
    # Determine risk
    if load_percentage > 110:
        risk_level = "critical"
        recommendations = [
            "Immediate action required - team member is overloaded",
            "Redistribute tasks to other team members",
            "Review priorities and defer non-critical work"
        ]
    elif load_percentage > 90:
        risk_level = "high"
        recommendations = [
            "Monitor closely - approaching overload",
            "Avoid assigning new tasks this week"
        ]
    else:
        risk_level = "low"
        recommendations = []
    
    analysis = {
        "id": uuid4().hex,
        "tenant_id": x_company_id,
        "user_id": user_id,
        "overload_risk_level": risk_level,
        "current_load_percentage": load_percentage,
        "recommendations": recommendations,
        "analyzed_at": datetime.utcnow()
    }
    
    team_risk_analyses_collection.update_one(
        {"user_id": user_id, "tenant_id": x_company_id},
        {"$set": analysis},
        upsert=True
    )
    
    if load_percentage > 90:
        risk = {
            "id": uuid4().hex,
            "tenant_id": x_company_id,
            "category": "team_overload",
            "level": risk_level,
            "status": "detected",
            "title": f"Team member overloaded ({load_percentage:.0f}%)",
            "description": f"Workload at {load_percentage:.0f}% capacity",
            "impact": "Risk of burnout, quality issues",
            "user_id": user_id,
            "probability": min(1.0, load_percentage / 100),
            "severity_score": min(100, load_percentage),
            "confidence": 0.95,
            "indicators": [f"{total_hours} hours worked this week"],
            "recommendations": recommendations,
            "detected_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        risks_collection.insert_one(risk)
    
    return {"message": "Team analysis complete", "analysis": analysis}


# ============= Risk Dashboard =============

@router.get("/dashboard")
async def get_risk_dashboard(
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get risk dashboard"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    # Get all active risks
    risks = list(risks_collection.find({
        "tenant_id": x_company_id,
        "status": {"$in": ["detected", "acknowledged"]}
    }).sort("severity_score", -1))
    
    for risk in risks:
        risk.pop("_id", None)
    
    # Count by level
    critical = len([r for r in risks if r.get("level") == "critical"])
    high = len([r for r in risks if r.get("level") == "high"])
    medium = len([r for r in risks if r.get("level") == "medium"])
    low = len([r for r in risks if r.get("level") == "low"])
    
    # Count by category
    by_category = {}
    for risk in risks:
        cat = risk.get("category", "unknown")
        by_category[cat] = by_category.get(cat, 0) + 1
    
    # New risks in last 24h
    yesterday = datetime.utcnow() - timedelta(days=1)
    new_risks_24h = len([r for r in risks if r.get("detected_at", datetime.min) > yesterday])
    
    dashboard = {
        "tenant_id": x_company_id,
        "total_risks": len(risks),
        "critical_risks": critical,
        "high_risks": high,
        "medium_risks": medium,
        "low_risks": low,
        "risks_by_category": by_category,
        "top_risks": risks[:10],
        "new_risks_24h": new_risks_24h,
        "generated_at": datetime.utcnow().isoformat()
    }
    
    return {"dashboard": dashboard}


@router.get("/risks")
async def get_all_risks(
    status: Optional[str] = None,
    level: Optional[str] = None,
    category: Optional[str] = None,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Get all risks with filters"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    query = {"tenant_id": x_company_id}
    if status:
        query["status"] = status
    if level:
        query["level"] = level
    if category:
        query["category"] = category
    
    risks = list(risks_collection.find(query).sort("severity_score", -1))
    for risk in risks:
        risk.pop("_id", None)
    
    return {"risks": risks, "count": len(risks)}


@router.put("/risks/{risk_id}/acknowledge")
async def acknowledge_risk(
    risk_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
):
    """Acknowledge a risk"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    result = risks_collection.update_one(
        {"id": risk_id, "tenant_id": x_company_id},
        {
            "$set": {
                "status": "acknowledged",
                "acknowledged_at": datetime.utcnow(),
                "acknowledged_by": x_user_id,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    return {"message": "Risk acknowledged"}


@router.put("/risks/{risk_id}/resolve")
async def resolve_risk(
    risk_id: str,
    current_user=Depends(get_current_user),
    x_company_id: Optional[str] = Header(None, alias="X-Company-ID")
):
    """Mark risk as resolved"""
    if not x_company_id:
        raise HTTPException(status_code=400, detail="X-Company-ID required")
    
    result = risks_collection.update_one(
        {"id": risk_id, "tenant_id": x_company_id},
        {
            "$set": {
                "status": "resolved",
                "resolved_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    return {"message": "Risk resolved"}
