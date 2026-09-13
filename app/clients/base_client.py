"""
app/clients/base_client.py

Resilient async HTTP client with timeouts, retries, and clean error handling.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)


class BaseAsyncHttpClient:
    """Async HTTP client base class supporting timeouts, retries, and graceful degradation."""

    def __init__(
        self,
        base_url: str = "",
        timeout_seconds: float = 3.0,
        max_retries: int = 2,
        backoff_factor: float = 0.5,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = httpx.Timeout(timeout_seconds)
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    async def get_json(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute an HTTP GET request with retries and return parsed JSON or None on failure.
        Never raises unhandled network exceptions to caller.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if self.base_url else endpoint
        attempt = 0

        while attempt <= self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params, headers=headers)
                    if response.status_code == 200:
                        return response.json()
                    elif 400 <= response.status_code < 500:
                        # Client error, retrying won't help
                        logger.warning(
                            "HTTP client error %s requesting %s: %s",
                            response.status_code,
                            url,
                            response.text,
                        )
                        return None
                    else:
                        logger.warning(
                            "HTTP server error %s requesting %s (attempt %d/%d)",
                            response.status_code,
                            url,
                            attempt + 1,
                            self.max_retries + 1,
                        )
            except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as exc:
                logger.warning(
                    "Network error requesting %s: %s (attempt %d/%d)",
                    url,
                    str(exc),
                    attempt + 1,
                    self.max_retries + 1,
                )
            except Exception as exc:
                logger.error("Unexpected error requesting %s: %s", url, str(exc))
                return None

            attempt += 1
            if attempt <= self.max_retries:
                sleep_time = self.backoff_factor * (2 ** (attempt - 1))
                await asyncio.sleep(sleep_time)

        return None
