import httpx

from src.core.config import settings
from src.core.logging import logger


class SlackConnector:
    """
    Handles outbound notifications to Slack via Webhooks.
    Uses connection pooling via a shared AsyncClient for efficiency.
    """

    _client: httpx.AsyncClient | None = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None or cls._client.is_closed:
            cls._client = httpx.AsyncClient(timeout=10.0)
        return cls._client

    @classmethod
    async def send_notification(cls, message: str, slack_id: str | None = None):
        if not settings.SLACK_WEBHOOK_URL:
            logger.warning("slack_notification_skipped", reason="NO_WEBHOOK_CONFIGURED")
            return

        # Handle @Mention formatting
        prefix = f"<@{slack_id}> " if slack_id else ""
        formatted_message = f"{prefix}{message}"

        client = cls.get_client()
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

    @classmethod
    async def close(cls):
        if cls._client and not cls._client.is_closed:
            await cls._client.aclose()
