"""
Unit tests for LINE webhook server.

Author: A.R. Ansari
Email: ansarirahim1@gmail.com
LinkedIn: https://www.linkedin.com/in/abdul-raheem-ansari-a6871320/
Project: Raspberry Pi Smart Monitoring Kit
"""

import pytest
import hmac
import hashlib
import json
from unittest.mock import Mock, patch, MagicMock
from src.line_api.webhook import WebhookServer


class TestWebhookServer:
    """Test cases for WebhookServer class."""
    
    @pytest.fixture
    def webhook_server(self):
        """Create webhook server instance for testing."""
        return WebhookServer(
            channel_access_token="test_token",
            channel_secret="test_secret",
            command_callback=Mock(),
            host="127.0.0.1",
            port=5001
        )
    
    def test_init_success(self, webhook_server):
        """Test successful initialization."""
        assert webhook_server.channel_access_token == "test_token"
        assert webhook_server.channel_secret == "test_secret"
        assert webhook_server.host == "127.0.0.1"
        assert webhook_server.port == 5001
        assert not webhook_server.running
    
    def test_init_missing_token(self):
        """Test initialization with missing token."""
        with pytest.raises(ValueError, match="channel_access_token is required"):
            WebhookServer(
                channel_access_token="",
                channel_secret="test_secret"
            )
    
    def test_init_missing_secret(self):
        """Test initialization with missing secret."""
        with pytest.raises(ValueError, match="channel_secret is required"):
            WebhookServer(
                channel_access_token="test_token",
                channel_secret=""
            )
    
    def test_process_command_stop(self, webhook_server):
        """Test processing stop command."""
        response = webhook_server._process_command("stop")
        assert "stopped" in response.lower()
        webhook_server.command_callback.assert_called_once_with("stop")
    
    def test_process_command_resume(self, webhook_server):
        """Test processing resume command."""
        response = webhook_server._process_command("resume")
        assert "resumed" in response.lower()
        webhook_server.command_callback.assert_called_once_with("resume")
    
    def test_process_command_status(self, webhook_server):
        """Test processing status command."""
        response = webhook_server._process_command("status")
        assert "running" in response.lower()
        webhook_server.command_callback.assert_called_once_with("status")
    
    def test_process_command_unknown(self, webhook_server):
        """Test processing unknown command."""
        response = webhook_server._process_command("invalid")
        assert "unknown" in response.lower()
        assert "stop" in response.lower()
        assert "resume" in response.lower()
        webhook_server.command_callback.assert_not_called()
    
    def test_is_running_initial(self, webhook_server):
        """Test is_running returns False initially."""
        assert not webhook_server.is_running()
    
    def test_webhook_endpoint_missing_signature(self, webhook_server):
        """Test webhook endpoint with missing signature."""
        with webhook_server.app.test_client() as client:
            response = client.post("/webhook", data="test")
            assert response.status_code == 400
    
    def test_webhook_endpoint_invalid_signature(self, webhook_server):
        """Test webhook endpoint with invalid signature."""
        with webhook_server.app.test_client() as client:
            response = client.post(
                "/webhook",
                data="test",
                headers={"X-Line-Signature": "invalid_signature"}
            )
            assert response.status_code == 400
    
    @patch('src.line_api.webhook.WebhookHandler')
    def test_webhook_endpoint_valid_signature(self, mock_handler, webhook_server):
        """Test webhook endpoint with valid signature."""
        # Mock handler to not raise exception
        mock_handler_instance = MagicMock()
        mock_handler.return_value = mock_handler_instance
        
        # Create new server with mocked handler
        server = WebhookServer(
            channel_access_token="test_token",
            channel_secret="test_secret"
        )
        
        with server.app.test_client() as client:
            body = json.dumps({"events": []})
            signature = "valid_signature"
            
            response = client.post(
                "/webhook",
                data=body,
                headers={"X-Line-Signature": signature}
            )
            
            # Should call handler.handle
            mock_handler_instance.handle.assert_called_once()
    
    def test_health_endpoint(self, webhook_server):
        """Test health check endpoint."""
        with webhook_server.app.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "ok"
            assert "running" in data
    
    def test_start_server(self, webhook_server):
        """Test starting server."""
        with patch.object(webhook_server, '_run_server'):
            webhook_server.start()
            assert webhook_server.running
            assert webhook_server.server_thread is not None
    
    def test_start_server_already_running(self, webhook_server):
        """Test starting server when already running."""
        webhook_server.running = True
        with patch.object(webhook_server, '_run_server'):
            webhook_server.start()
            # Should not create new thread
            assert webhook_server.server_thread is None
    
    def test_stop_server(self, webhook_server):
        """Test stopping server."""
        webhook_server.running = True
        webhook_server.stop()
        assert not webhook_server.running

