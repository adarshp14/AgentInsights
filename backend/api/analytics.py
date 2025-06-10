"""
Analytics API for organization metrics and insights
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from database.database import get_db
from database.models import Document, User
from auth.clerk_auth import get_current_user_compatible

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = logging.getLogger(__name__)

def get_current_user(
    user_info: Dict[str, Any] = Depends(get_current_user_compatible)
) -> Dict[str, Any]:
    """Get current authenticated user"""
    return user_info

@router.get("/overview")
async def get_analytics_overview(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics overview for organization"""
    try:
        org_id = current_user["org_id"]
        
        # Document Statistics
        total_documents = db.query(Document).filter(
            Document.org_id == org_id
        ).count()
        
        processed_documents = db.query(Document).filter(
            Document.org_id == org_id,
            Document.processing_status == "completed"
        ).count()
        
        processing_documents = db.query(Document).filter(
            Document.org_id == org_id,
            Document.processing_status == "processing"
        ).count()
        
        failed_documents = db.query(Document).filter(
            Document.org_id == org_id,
            Document.processing_status == "failed"
        ).count()
        
        # Storage Statistics
        total_storage = db.query(func.sum(Document.file_size)).filter(
            Document.org_id == org_id
        ).scalar() or 0
        
        total_chunks = db.query(func.sum(Document.chunks_created)).filter(
            Document.org_id == org_id,
            Document.processing_status == "completed"
        ).scalar() or 0
        
        # User Statistics
        total_users = db.query(User).filter(
            User.org_id == org_id,
            User.is_active == True
        ).count()
        
        admin_users = db.query(User).filter(
            User.org_id == org_id,
            User.role == "admin",
            User.is_active == True
        ).count()
        
        # Recent Activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_documents = db.query(Document).filter(
            Document.org_id == org_id,
            Document.upload_date >= thirty_days_ago
        ).count()
        
        recent_users = db.query(User).filter(
            User.org_id == org_id,
            User.created_at >= thirty_days_ago
        ).count()
        
        # Document Processing Health
        success_rate = 0
        if total_documents > 0:
            success_rate = round((processed_documents / total_documents) * 100, 1)
        
        return {
            "organization": {
                "org_id": org_id,
                "total_users": total_users,
                "admin_users": admin_users,
                "employee_users": total_users - admin_users
            },
            "documents": {
                "total": total_documents,
                "processed": processed_documents,
                "processing": processing_documents,
                "failed": failed_documents,
                "success_rate": success_rate
            },
            "storage": {
                "total_size_bytes": total_storage,
                "total_size_mb": round(total_storage / (1024 * 1024), 2),
                "total_chunks": total_chunks,
                "avg_chunks_per_doc": round(total_chunks / max(processed_documents, 1), 1)
            },
            "activity": {
                "documents_uploaded_30d": recent_documents,
                "users_added_30d": recent_users,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching analytics overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching analytics: {str(e)}"
        )

@router.get("/documents/timeline")
async def get_documents_timeline(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 30
):
    """Get document upload timeline for the last N days"""
    try:
        org_id = current_user["org_id"]
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query documents grouped by date
        timeline_query = db.query(
            func.date(Document.upload_date).label('date'),
            func.count(Document.document_id).label('count'),
            func.sum(Document.file_size).label('total_size')
        ).filter(
            Document.org_id == org_id,
            Document.upload_date >= start_date
        ).group_by(
            func.date(Document.upload_date)
        ).order_by(
            func.date(Document.upload_date)
        ).all()
        
        # Format timeline data
        timeline_data = []
        for row in timeline_query:
            timeline_data.append({
                "date": row.date.isoformat(),
                "documents_uploaded": row.count,
                "total_size_mb": round((row.total_size or 0) / (1024 * 1024), 2)
            })
        
        return {
            "timeline": timeline_data,
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching documents timeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching timeline: {str(e)}"
        )

@router.get("/documents/types")
async def get_document_types_breakdown(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get breakdown of document types in organization"""
    try:
        org_id = current_user["org_id"]
        
        # Query document types
        types_query = db.query(
            Document.file_type,
            func.count(Document.document_id).label('count'),
            func.sum(Document.file_size).label('total_size'),
            func.avg(Document.file_size).label('avg_size')
        ).filter(
            Document.org_id == org_id
        ).group_by(
            Document.file_type
        ).order_by(
            func.count(Document.document_id).desc()
        ).all()
        
        # Format breakdown data
        breakdown_data = []
        total_docs = 0
        total_size = 0
        
        for row in types_query:
            count = row.count
            size = row.total_size or 0
            total_docs += count
            total_size += size
            
            breakdown_data.append({
                "file_type": row.file_type,
                "document_count": count,
                "total_size_mb": round(size / (1024 * 1024), 2),
                "average_size_mb": round((row.avg_size or 0) / (1024 * 1024), 2)
            })
        
        # Calculate percentages
        for item in breakdown_data:
            item["percentage"] = round((item["document_count"] / max(total_docs, 1)) * 100, 1)
        
        return {
            "breakdown": breakdown_data,
            "summary": {
                "total_documents": total_docs,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "unique_types": len(breakdown_data)
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching document types: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching document types: {str(e)}"
        )

@router.get("/processing/health")
async def get_processing_health(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document processing health metrics"""
    try:
        org_id = current_user["org_id"]
        
        # Processing status breakdown
        status_query = db.query(
            Document.processing_status,
            func.count(Document.document_id).label('count')
        ).filter(
            Document.org_id == org_id
        ).group_by(
            Document.processing_status
        ).all()
        
        status_breakdown = {}
        total_documents = 0
        
        for row in status_query:
            status_breakdown[row.processing_status] = row.count
            total_documents += row.count
        
        # Calculate processing metrics
        completed = status_breakdown.get("completed", 0)
        processing = status_breakdown.get("processing", 0)
        failed = status_breakdown.get("failed", 0)
        
        success_rate = round((completed / max(total_documents, 1)) * 100, 1)
        failure_rate = round((failed / max(total_documents, 1)) * 100, 1)
        
        # Average processing time (mock data - would need processing_time field)
        avg_processing_time = "45 seconds"  # This would be calculated from actual data
        
        # Recent failures for debugging
        recent_failures = db.query(Document).filter(
            Document.org_id == org_id,
            Document.processing_status == "failed"
        ).order_by(Document.upload_date.desc()).limit(5).all()
        
        failure_details = []
        for doc in recent_failures:
            failure_details.append({
                "filename": doc.original_filename,
                "upload_date": doc.upload_date.isoformat(),
                "file_type": doc.file_type,
                "file_size_mb": round(doc.file_size / (1024 * 1024), 2)
            })
        
        return {
            "health_metrics": {
                "total_documents": total_documents,
                "success_rate": success_rate,
                "failure_rate": failure_rate,
                "currently_processing": processing,
                "average_processing_time": avg_processing_time
            },
            "status_breakdown": status_breakdown,
            "recent_failures": failure_details,
            "recommendations": get_processing_recommendations(success_rate, failure_rate, processing)
        }
        
    except Exception as e:
        logger.error(f"Error fetching processing health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching processing health: {str(e)}"
        )

def get_processing_recommendations(success_rate: float, failure_rate: float, processing_count: int) -> List[str]:
    """Generate recommendations based on processing metrics"""
    recommendations = []
    
    if success_rate < 80:
        recommendations.append("Document processing success rate is below 80%. Consider checking file formats and sizes.")
    
    if failure_rate > 20:
        recommendations.append("High failure rate detected. Review failed documents and ensure supported file formats.")
    
    if processing_count > 10:
        recommendations.append("Many documents are currently processing. Consider uploading smaller batches.")
    
    if success_rate > 95:
        recommendations.append("Excellent processing health! Your document pipeline is performing optimally.")
    
    if not recommendations:
        recommendations.append("Processing health looks good. Continue monitoring for optimal performance.")
    
    return recommendations