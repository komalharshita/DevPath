# utils/redis_service import
import os
import time
from utils.rate_limiter import redis_client # Reuses our core app redis connection pool
from utils.data_loader import find_project_by_id

HISTORY_MAX_SIZE = 10 # Cap the history timeline to save memory footprint

def track_user_history(user_id: str, project_id: int):
    """
    Saves a historical timeline log of viewed projects inside Redis ZSET.
    """
    if not redis_client:
        return
        
    history_key = f"user:history:{user_id}"
    current_timestamp = int(time.time())
    
    try:
        pipeline = redis_client.pipeline()
        # Add project item with current timestamp score
        pipeline.zadd(history_key, {str(project_id): current_timestamp})
        # Keep only the newest items (removes old indices trailing past our limit threshold)
        pipeline.zremrangebyrank(history_key, 0, -(HISTORY_MAX_SIZE + 1))
        # Add an expiration time of 30 days on inactivity so data cleans itself up over time
        pipeline.expire(history_key, 2592000) 
        pipeline.execute()
    except Exception as e:
        print(f"[Redis Cache Error] Could not register history log pipeline: {e}")


def get_user_cached_suggestions(user_id: str):
    """
    Fetches real-time suggestions based on recently viewed items from Redis.
    If no history exists, returns fallback empty structures safely.
    """
    if not redis_client:
        return []
        
    history_key = f"user:history:{user_id}"
    try:
        # Retrieve the latest 3 project IDs from the user's history
        recent_project_ids = redis_client.zrevrange(history_key, 0, 2)
        
        if not recent_project_ids:
            return []
            
        # Placeholder / Mock Recommendation Strategy:
        # In production, a background worker or ML microservice would ingest the Kafka topics 
        # and populate a `user:suggestions:{user_id}` Redis key. 
        # For now, we dynamically pull the project names from the current active database layer.
        recommendations = []
        for pid in recent_project_ids:
            proj = find_project_by_id(int(pid))
            if proj:
                recommendations.append({
                    "id": proj.get("id"),
                    "title": proj.get("title"),
                    "reason": "Based on your recent interest"
                })
        return recommendations
        
    except Exception as e:
        print(f"[Redis Cache Error] Could not retrieve recommendations context: {e}")
        return []