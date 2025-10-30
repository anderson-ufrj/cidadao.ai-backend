"""
Grafana Cloud Metrics Pusher

Envia métricas Prometheus para Grafana Cloud via Remote Write.

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brasil
"""

import asyncio
import logging
import os
from contextlib import suppress
from typing import Any

from prometheus_client import REGISTRY, push_to_gateway
from prometheus_client.exposition import basic_auth_handler

logger = logging.getLogger(__name__)


class GrafanaCloudPusher:
    """Push metrics to Grafana Cloud Prometheus."""

    def __init__(self) -> None:
        self.enabled = os.getenv("GRAFANA_CLOUD_ENABLED", "false").lower() == "true"
        self.url = os.getenv("GRAFANA_CLOUD_URL", "")
        self.user = os.getenv("GRAFANA_CLOUD_USER", "")
        self.key = os.getenv("GRAFANA_CLOUD_KEY", "")
        self.interval = int(os.getenv("METRICS_PUSH_INTERVAL", "60"))
        self.timeout = int(os.getenv("METRICS_PUSH_TIMEOUT", "10"))

        self._task: asyncio.Task | None = None
        self._running = False

    def _validate_config(self) -> bool:
        """Validate Grafana Cloud configuration."""
        if not self.enabled:
            logger.info("Grafana Cloud push disabled")
            return False

        if not all([self.url, self.user, self.key]):
            logger.warning(
                "Grafana Cloud enabled but missing credentials. "
                "Set GRAFANA_CLOUD_URL, GRAFANA_CLOUD_USER, GRAFANA_CLOUD_KEY"
            )
            return False

        return True

    async def push_metrics(self) -> bool:
        """
        Push metrics to Grafana Cloud.

        Returns:
            True if successful, False otherwise
        """
        if not self._validate_config():
            return False

        try:
            # Extract hostname from URL for gateway
            # URL: https://prometheus-prod-XX.grafana.net/api/prom/push
            # Gateway: prometheus-prod-XX.grafana.net:443
            gateway = self.url.replace("https://", "").replace("http://", "")
            gateway = gateway.split("/")[0]  # Remove path

            # Create auth handler
            # ruff: noqa: ANN401
            def auth_handler(
                url: str, method: str, timeout: Any, headers: Any, data: Any
            ) -> Any:
                return basic_auth_handler(
                    url, method, timeout, headers, data, self.user, self.key
                )

            # Push to gateway
            push_to_gateway(
                gateway=f"{gateway}:443",
                job="cidadao-ai-backend",
                registry=REGISTRY,
                handler=auth_handler,
                timeout=self.timeout,
            )

            logger.debug("Metrics pushed to Grafana Cloud successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to push metrics to Grafana Cloud: {e}")
            return False

    async def _push_loop(self) -> None:
        """Background loop to push metrics periodically."""
        logger.info(
            f"Starting Grafana Cloud metrics push loop (interval: {self.interval}s)"
        )

        while self._running:
            try:
                await self.push_metrics()
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                logger.info("Grafana Cloud push loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in push loop: {e}")
                await asyncio.sleep(self.interval)

    async def start(self) -> None:
        """Start periodic metrics push."""
        if not self._validate_config():
            logger.info("Grafana Cloud push not started (disabled or misconfigured)")
            return

        if self._running:
            logger.warning("Grafana Cloud pusher already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._push_loop())
        logger.info("Grafana Cloud metrics pusher started")

    async def stop(self) -> None:
        """Stop periodic metrics push."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

        logger.info("Grafana Cloud metrics pusher stopped")


# Global instance
grafana_pusher = GrafanaCloudPusher()
