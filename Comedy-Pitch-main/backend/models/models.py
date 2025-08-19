# Central models file - imports all models to ensure relationships are properly set up
from models.user import User
from models.video import Video
from models.like import Like
from models.analytics import AnalyticsData

# Export all models
__all__ = ["User", "Video", "Like", "AnalyticsData"] 