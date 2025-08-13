"""Notification service for alerts and updates."""

from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class NotificationLevel(Enum):
    """Notification severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NotificationService:
    """Service for managing notifications and alerts."""
    
    def __init__(self):
        self._notifications = []
        self._subscribers = {}
    
    async def send_notification(
        self, 
        message: str, 
        level: NotificationLevel = NotificationLevel.INFO,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Send a notification."""
        notification = {
            "id": len(self._notifications),
            "message": message,
            "level": level.value,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "read": False
        }
        
        self._notifications.append(notification)
        return True
    
    async def send_anomaly_alert(self, anomaly_data: Dict) -> bool:
        """Send alert for detected anomaly."""
        message = f"Anomalia detectada: {anomaly_data.get('description', 'Sem descrição')}"
        return await self.send_notification(
            message, 
            NotificationLevel.WARNING,
            {"type": "anomaly", "data": anomaly_data}
        )
    
    async def send_analysis_complete(self, analysis_id: str, results: Dict) -> bool:
        """Send notification when analysis is complete."""
        message = f"Análise {analysis_id} concluída com {results.get('total_items', 0)} itens processados"
        return await self.send_notification(
            message,
            NotificationLevel.INFO,
            {"type": "analysis_complete", "analysis_id": analysis_id, "results": results}
        )
    
    def get_notifications(self, unread_only: bool = False) -> List[Dict]:
        """Get notifications."""
        if unread_only:
            return [n for n in self._notifications if not n["read"]]
        return self._notifications
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark notification as read."""
        for notification in self._notifications:
            if notification["id"] == notification_id:
                notification["read"] = True
                return True
        return False
    
    def clear_notifications(self) -> None:
        """Clear all notifications."""
        self._notifications.clear()
    
    def subscribe(self, subscriber_id: str, callback) -> bool:
        """Subscribe to notifications."""
        # TODO: Implement subscription system
        self._subscribers[subscriber_id] = callback
        return True
    
    def unsubscribe(self, subscriber_id: str) -> bool:
        """Unsubscribe from notifications."""
        return self._subscribers.pop(subscriber_id, None) is not None