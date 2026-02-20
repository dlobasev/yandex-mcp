"""Unified API client for Yandex Direct and Metrika."""

import os
from typing import Any

import httpx

from yandex_mcp.config import (
    DEFAULT_TIMEOUT,
    REPORTS_TIMEOUT,
    YANDEX_DIRECT_API_URL,
    YANDEX_DIRECT_API_URL_V501,
    YANDEX_DIRECT_SANDBOX_URL,
    YANDEX_METRIKA_API_URL,
)


class YandexAPIClient:
    """Unified client for Yandex Direct and Metrika APIs."""

    def __init__(self) -> None:
        self.direct_token = os.environ.get("YANDEX_DIRECT_TOKEN", "")
        self.metrika_token = os.environ.get("YANDEX_METRIKA_TOKEN", "")
        self.unified_token = os.environ.get("YANDEX_TOKEN", "")
        self.client_login = os.environ.get("YANDEX_CLIENT_LOGIN", "")
        self.use_sandbox = os.environ.get("YANDEX_USE_SANDBOX", "false").lower() == "true"

    def _get_direct_token(self) -> str:
        return self.direct_token or self.unified_token

    def _get_metrika_token(self) -> str:
        return self.metrika_token or self.unified_token

    def _get_direct_url(self, use_v501: bool = False) -> str:
        if self.use_sandbox:
            return YANDEX_DIRECT_SANDBOX_URL
        return YANDEX_DIRECT_API_URL_V501 if use_v501 else YANDEX_DIRECT_API_URL

    async def direct_request(
        self,
        service: str,
        method: str,
        params: dict[str, Any],
        use_v501: bool = False,
    ) -> dict[str, Any]:
        """Make a request to Yandex Direct API."""
        token = self._get_direct_token()
        if not token:
            raise ValueError(
                "Yandex Direct API token not configured. "
                "Set YANDEX_DIRECT_TOKEN or YANDEX_TOKEN environment variable."
            )

        url = f"{self._get_direct_url(use_v501)}/{service}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept-Language": "ru",
            "Content-Type": "application/json",
        }

        if self.client_login:
            headers["Client-Login"] = self.client_login

        payload = {
            "method": method,
            "params": params,
        }

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()

    async def direct_report_request(
        self,
        report_definition: dict[str, Any],
    ) -> httpx.Response:
        """Make a request to Yandex Direct Reports API.

        Returns the raw response since the Reports API returns TSV, not JSON.
        """
        token = self._get_direct_token()
        if not token:
            raise ValueError("Yandex Direct API token not configured.")

        url = f"{self._get_direct_url()}/reports"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept-Language": "ru",
            "Content-Type": "application/json",
            "processingMode": "auto",
            "returnMoneyInMicros": "false",
            "skipReportHeader": "true",
            "skipColumnHeader": "false",
            "skipReportSummary": "true",
        }

        if self.client_login:
            headers["Client-Login"] = self.client_login

        async with httpx.AsyncClient(timeout=REPORTS_TIMEOUT) as client:
            response = await client.post(
                url,
                json={"params": report_definition},
                headers=headers,
            )
            return response

    async def metrika_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a request to Yandex Metrika API."""
        token = self._get_metrika_token()
        if not token:
            raise ValueError(
                "Yandex Metrika API token not configured. "
                "Set YANDEX_METRIKA_TOKEN or YANDEX_TOKEN environment variable."
            )

        url = f"{YANDEX_METRIKA_API_URL}{endpoint}"
        headers = {
            "Authorization": f"OAuth {token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            if method == "GET":
                response = await client.get(url, params=params, headers=headers)
            elif method == "POST":
                response = await client.post(url, json=data, params=params, headers=headers)
            elif method == "PUT":
                response = await client.put(url, json=data, params=params, headers=headers)
            elif method == "DELETE":
                response = await client.delete(url, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            if response.status_code == 204:
                return {"success": True}

            return response.json()


api_client = YandexAPIClient()
