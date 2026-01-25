import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from src.core.slack import SlackConnector
from src.core.config import settings

@pytest.mark.asyncio
async def test_slack_no_webhook_url():
    """Test that SlackConnector skips notification if webhook URL is not set."""
    with patch("src.core.slack.settings") as mock_settings:
        mock_settings.SLACK_WEBHOOK_URL = None
        with patch("src.core.slack.logger") as mock_logger:
            await SlackConnector.send_notification("test message")
            mock_logger.warning.assert_called_once_with(
                "slack_notification_skipped", reason="NO_WEBHOOK_CONFIGURED"
            )

@pytest.mark.asyncio
async def test_slack_success():
    """Test successful Slack notification."""
    with patch("src.core.slack.settings") as mock_settings:
        mock_settings.SLACK_WEBHOOK_URL = "http://fake-webhook.com"
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response
            
            await SlackConnector.send_notification("test message", slack_id="U123")
            
            mock_post.assert_called_once_with(
                "http://fake-webhook.com",
                json={"text": "<@U123> test message"}
            )
            mock_response.raise_for_status.assert_called_once()

@pytest.mark.asyncio
async def test_slack_failure():
    """Test Slack notification failure handling."""
    with patch("src.core.slack.settings") as mock_settings:
        mock_settings.SLACK_WEBHOOK_URL = "http://fake-webhook.com"
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("HTTP Error")
            with patch("src.core.slack.logger") as mock_logger:
                await SlackConnector.send_notification("test message")
                mock_logger.error.assert_called_once_with(
                    "slack_notification_failed", error="HTTP Error"
                )
