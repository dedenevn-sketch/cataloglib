"""Базовый async HTTP-клиент с retry и экспоненциальным backoff."""

import asyncio
import logging
from abc import ABC, abstractmethod

import httpx


class BaseApiClient(ABC):
    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        retries: int = 3,
        backoff: float = 0.5,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self._client = httpx.AsyncClient(timeout=self.timeout)
        self.logger = logging.getLogger(self.client_name())

    @abstractmethod
    def client_name(self) -> str: ...

    def _build_url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    async def _request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        json: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
        url = self._build_url(path)

        for attempt in range(self.retries):
            try:
                self.logger.debug("%s %s params=%s", method, url, params)
                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                if attempt == self.retries - 1:
                    self.logger.error("Timeout after %s attempts", self.retries)
                    raise
                wait_time = self.backoff * (2 ** attempt)
                self.logger.warning("Timeout, retrying in %ss...", wait_time)
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as exc:
                if exc.response.status_code >= 500 and attempt < self.retries - 1:
                    wait_time = self.backoff * (2 ** attempt)
                    self.logger.warning(
                        "Server error %s, retrying in %ss...",
                        exc.response.status_code,
                        wait_time,
                    )
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error("HTTP error: %s", exc)
                    raise

        raise httpx.HTTPError(f"Request to {url} failed after {self.retries} attempts")

    async def _get(self, path: str, **kwargs) -> dict:
        return await self._request("GET", path, **kwargs)

    async def close(self) -> None:
        await self._client.aclose()
