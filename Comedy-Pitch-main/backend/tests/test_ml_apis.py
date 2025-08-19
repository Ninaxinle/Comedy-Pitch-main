import pytest
import json
from unittest.mock import patch

class TestMLScoreResults:
    """Test ML score results submission"""
    
    def test_submit_ml_results_success(self, client, db_session, test_video):
        """Test successful ML results submission"""
        ml_data = {
            "video_id": test_video.id,
            "processing_version": "v1.2.0",
            "transcript": [
                {
                    "text": "Welcome to my comedy show",
                    "start_time": 0.0,
                    "end_time": 3.5,
                    "funniness_score": 0.2
                },
                {
                    "text": "Here's my first joke...",
                    "start_time": 3.5,
                    "end_time": 8.0,
                    "funniness_score": 0.8
                },
                {
                    "text": "And another funny story",
                    "start_time": 8.0,
                    "end_time": 12.5,
                    "funniness_score": 0.9
                }
            ],
            "overall_funniness_score": 0.75,
            "laughter_timestamps": [
                {
                    "timestamp": 7.5,
                    "duration": 2.0,
                    "intensity": 0.8
                },
                {
                    "timestamp": 11.0,
                    "duration": 1.5,
                    "intensity": 0.95
                }
            ],
            "confidence_score": 0.92,
            "processing_duration": 45.3,
            "word_count": 150,
            "speaking_rate": 120.5
        }
        
        response = client.post("/api/ml/score-results", json=ml_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "ML results processed successfully"
        assert data["video_id"] == test_video.id
        assert "analytics_id" in data
        
        # Verify analytics data was created
        from models.models import AnalyticsData
        analytics = db_session.query(AnalyticsData).filter(
            AnalyticsData.video_id == test_video.id
        ).first()
        
        assert analytics is not None
        assert analytics.overall_funniness_score == 0.75
        assert analytics.processing_version == "v1.2.0"
        assert analytics.confidence_score == 0.92
        assert analytics.word_count == 150
        assert analytics.speaking_rate == 120.5
        
        # Check transcript structure
        assert len(analytics.transcript) == 3
        assert analytics.transcript[0]["text"] == "Welcome to my comedy show"
        assert analytics.transcript[1]["funniness_score"] == 0.8
        assert analytics.transcript[2]["end_time"] == 12.5
        
        # Check laughter timestamps
        assert len(analytics.laughter_timestamps) == 2
        assert analytics.laughter_timestamps[0]["timestamp"] == 7.5
        assert analytics.laughter_timestamps[1]["intensity"] == 0.95
        
        # Verify video status was updated
        db_session.refresh(test_video)
        assert test_video.is_processed is True
        assert test_video.processing_status == "completed"
        
    def test_submit_ml_results_update_existing(self, client, db_session, test_video):
        """Test updating existing analytics data"""
        from models.models import AnalyticsData
        
        # Create existing analytics
        existing_analytics = AnalyticsData(
            video_id=test_video.id,
            overall_funniness_score=0.5,
            processing_version="v1.0.0"
        )
        db_session.add(existing_analytics)
        db_session.commit()
        analytics_id = existing_analytics.id
        
        # Submit new results
        ml_data = {
            "video_id": test_video.id,
            "processing_version": "v1.2.0",
            "transcript": [
                {
                    "text": "Updated transcript",
                    "start_time": 0.0,
                    "end_time": 5.0,
                    "funniness_score": 0.7
                }
            ],
            "overall_funniness_score": 0.85,
            "confidence_score": 0.95
        }
        
        response = client.post("/api/ml/score-results", json=ml_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["analytics_id"] == analytics_id  # Same ID, updated record
        
        # Verify the record was updated, not replaced
        db_session.refresh(existing_analytics)
        assert existing_analytics.overall_funniness_score == 0.85
        assert existing_analytics.processing_version == "v1.2.0"
        assert existing_analytics.confidence_score == 0.95
        assert len(existing_analytics.transcript) == 1
        
    def test_submit_ml_results_video_not_found(self, client):
        """Test ML results submission for non-existent video"""
        ml_data = {
            "video_id": 99999,
            "processing_version": "v1.0.0",
            "transcript": [],
            "overall_funniness_score": 0.5
        }
        
        response = client.post("/api/ml/score-results", json=ml_data)
        assert response.status_code == 404
        assert "Video not found" in response.json()["detail"]
        
    def test_submit_ml_results_invalid_data(self, client, test_video):
        """Test ML results submission with invalid data"""
        ml_data = {
            "video_id": test_video.id,
            "processing_version": "v1.0.0",
            "transcript": [],
            "overall_funniness_score": 1.5  # Invalid: should be <= 1.0
        }
        
        response = client.post("/api/ml/score-results", json=ml_data)
        assert response.status_code == 422  # Validation error
        
    def test_submit_ml_results_minimal_data(self, client, test_video, db_session):
        """Test ML results submission with minimal required data"""
        ml_data = {
            "video_id": test_video.id,
            "processing_version": "v1.0.0",
            "transcript": [
                {
                    "text": "Simple transcript",
                    "start_time": 0.0,
                    "end_time": 5.0
                }
            ],
            "overall_funniness_score": 0.6
        }
        
        response = client.post("/api/ml/score-results", json=ml_data)
        
        assert response.status_code == 200
        
        # Verify optional fields are handled correctly
        from models.models import AnalyticsData
        analytics = db_session.query(AnalyticsData).filter(
            AnalyticsData.video_id == test_video.id
        ).first()
        
        assert analytics.overall_funniness_score == 0.6
        assert analytics.laughter_timestamps is None
        assert analytics.confidence_score is None
        assert analytics.word_count is None

class TestMLProcessingStatus:
    """Test ML processing status updates"""
    
    def test_update_processing_status_success(self, client, test_video, db_session):
        """Test successful processing status update"""
        status_data = {
            "video_id": test_video.id,
            "status": "processing"
        }
        
        response = client.post("/api/ml/processing-status", json=status_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Processing status updated successfully"
        assert data["video_id"] == test_video.id
        assert data["status"] == "processing"
        
        # Verify video status was updated
        db_session.refresh(test_video)
        assert test_video.processing_status == "processing"
        assert test_video.is_processed is False
        
    def test_update_processing_status_completed(self, client, test_video, db_session):
        """Test updating status to completed"""
        status_data = {
            "video_id": test_video.id,
            "status": "completed"
        }
        
        response = client.post("/api/ml/processing-status", json=status_data)
        assert response.status_code == 200
        
        db_session.refresh(test_video)
        assert test_video.processing_status == "completed"
        assert test_video.is_processed is True
        
    def test_update_processing_status_failed(self, client, test_video, db_session):
        """Test updating status to failed"""
        status_data = {
            "video_id": test_video.id,
            "status": "failed",
            "error_message": "Processing failed due to audio quality"
        }
        
        response = client.post("/api/ml/processing-status", json=status_data)
        assert response.status_code == 200
        
        db_session.refresh(test_video)
        assert test_video.processing_status == "failed"
        assert test_video.is_processed is False
        
    def test_update_processing_status_video_not_found(self, client):
        """Test status update for non-existent video"""
        status_data = {
            "video_id": 99999,
            "status": "processing"
        }
        
        response = client.post("/api/ml/processing-status", json=status_data)
        assert response.status_code == 404

class TestGetProcessingStatus:
    """Test processing status retrieval"""
    
    def test_get_processing_status_success(self, client, test_video, db_session):
        """Test successful processing status retrieval"""
        from models.models import AnalyticsData
        
        # Update video status
        test_video.processing_status = "completed"
        test_video.is_processed = True
        
        # Add analytics
        analytics = AnalyticsData(
            video_id=test_video.id,
            processing_version="v1.0.0",
            overall_funniness_score=0.7
        )
        db_session.add(analytics)
        db_session.commit()
        
        response = client.get(f"/api/ml/video/{test_video.id}/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["video_id"] == test_video.id
        assert data["processing_status"] == "completed"
        assert data["is_processed"] is True
        assert data["has_analytics"] is True
        assert data["processing_version"] == "v1.0.0"
        
    def test_get_processing_status_no_analytics(self, client, test_video):
        """Test processing status when no analytics exist"""
        response = client.get(f"/api/ml/video/{test_video.id}/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["video_id"] == test_video.id
        assert data["processing_status"] == "pending"  # Default status
        assert data["is_processed"] is False
        assert data["has_analytics"] is False
        assert data["processing_version"] is None
        
    def test_get_processing_status_video_not_found(self, client):
        """Test processing status for non-existent video"""
        response = client.get("/api/ml/video/99999/status")
        assert response.status_code == 404

class TestMLHealthCheck:
    """Test ML health check endpoint"""
    
    def test_ml_health_check(self, client):
        """Test ML health check endpoint"""
        response = client.get("/api/ml/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "ml_processing"
        assert "routes" in data
        assert "/score-results" in data["routes"]
        assert "/processing-status" in data["routes"]

class TestMLWorkflow:
    """Test complete ML processing workflow"""
    
    def test_complete_ml_workflow(self, client, test_video, db_session):
        """Test complete ML workflow: status update -> processing -> results"""
        
        # Step 1: Update status to processing
        status_data = {
            "video_id": test_video.id,
            "status": "processing"
        }
        
        response = client.post("/api/ml/processing-status", json=status_data)
        assert response.status_code == 200
        
        # Verify status
        response = client.get(f"/api/ml/video/{test_video.id}/status")
        assert response.status_code == 200
        assert response.json()["processing_status"] == "processing"
        
        # Step 2: Submit ML results
        ml_data = {
            "video_id": test_video.id,
            "processing_version": "v1.0.0",
            "transcript": [
                {
                    "text": "This is a test transcript",
                    "start_time": 0.0,
                    "end_time": 5.0,
                    "funniness_score": 0.7
                }
            ],
            "overall_funniness_score": 0.7,
            "laughter_timestamps": [
                {
                    "timestamp": 4.0,
                    "duration": 1.0,
                    "intensity": 0.8
                }
            ],
            "confidence_score": 0.9,
            "processing_duration": 30.5
        }
        
        response = client.post("/api/ml/score-results", json=ml_data)
        assert response.status_code == 200
        
        # Step 3: Verify final status
        response = client.get(f"/api/ml/video/{test_video.id}/status")
        assert response.status_code == 200
        
        final_status = response.json()
        assert final_status["processing_status"] == "completed"
        assert final_status["is_processed"] is True
        assert final_status["has_analytics"] is True
        assert final_status["processing_version"] == "v1.0.0"
        
        # Step 4: Verify analytics data in database
        from models.models import AnalyticsData
        analytics = db_session.query(AnalyticsData).filter(
            AnalyticsData.video_id == test_video.id
        ).first()
        
        assert analytics is not None
        assert analytics.overall_funniness_score == 0.7
        assert len(analytics.transcript) == 1
        assert len(analytics.laughter_timestamps) == 1

class TestMLErrorHandling:
    """Test ML API error handling"""
    
    def test_ml_results_with_processing_error(self, client, test_video):
        """Test handling of processing errors"""
        # First mark as failed
        status_data = {
            "video_id": test_video.id,
            "status": "failed",
            "error_message": "Audio quality too poor for analysis"
        }
        
        response = client.post("/api/ml/processing-status", json=status_data)
        assert response.status_code == 200
        
        # Try to submit results anyway (should still work)
        ml_data = {
            "video_id": test_video.id,
            "processing_version": "v1.0.0",
            "transcript": [],
            "overall_funniness_score": 0.0
        }
        
        response = client.post("/api/ml/score-results", json=ml_data)
        assert response.status_code == 200  # Should succeed and mark as completed
        
    def test_invalid_funniness_scores(self, client, test_video):
        """Test validation of funniness scores"""
        test_cases = [
            {"overall_funniness_score": -0.1},  # Below 0
            {"overall_funniness_score": 1.1},   # Above 1
            {
                "overall_funniness_score": 0.5,
                "transcript": [
                    {
                        "text": "Test",
                        "start_time": 0.0,
                        "end_time": 1.0,
                        "funniness_score": -0.1  # Invalid segment score
                    }
                ]
            }
        ]
        
        for invalid_data in test_cases:
            ml_data = {
                "video_id": test_video.id,
                "processing_version": "v1.0.0",
                "transcript": invalid_data.get("transcript", []),
                **{k: v for k, v in invalid_data.items() if k != "transcript"}
            }
            
            response = client.post("/api/ml/score-results", json=ml_data)
            assert response.status_code == 422  # Validation error
            
    def test_confidence_score_validation(self, client, test_video):
        """Test confidence score validation"""
        ml_data = {
            "video_id": test_video.id,
            "processing_version": "v1.0.0",
            "transcript": [],
            "overall_funniness_score": 0.5,
            "confidence_score": 1.5  # Invalid: should be <= 1.0
        }
        
        response = client.post("/api/ml/score-results", json=ml_data)
        assert response.status_code == 422 