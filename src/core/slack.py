import httpx

from src.core.config import settings
from src.core.logging import logger


class SlackConnector:
    """
    Handles outbound notifications to Slack via Webhooks.
    Designed for 'Fire and Forget' non-blocking updates.
    """

    @classmethod
    async def send_notification(cls, message: str, slack_id: str | None = None):
        if not settings.SLACK_WEBHOOK_URL:
            logger.warning("slack_notification_skipped", reason="NO_WEBHOOK_CONFIGURED")
            return

        # Handle @Mention formatting
        prefix = f"<@{slack_id}> " if slack_id else ""
        formatted_message = f"{prefix}{message}"

        async with httpx.AsyncClient() as client:
            try:
                payload = {"text": formatted_message}
                response = await client.post(settings.SLACK_WEBHOOK_URL, json=payload)
                response.raise_for_status()
                logger.info(
                    "slack_notification_sent",
                    status="success",
                    mentioned=bool(slack_id),
                )
            except Exception as e:
                logger.error("slack_notification_failed", error=str(e))
