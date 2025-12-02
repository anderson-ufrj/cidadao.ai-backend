"""
APM integrations for popular monitoring platforms.

This module provides pre-built integrations for common APM tools
like New Relic, Datadog, Dynatrace, and Elastic APM.
"""

from typing import Any

import httpx

from src.core import json_utils
from src.infrastructure.observability import get_structured_logger

from .hooks import APMError, APMEvent, APMPerformanceMetric, apm_hooks

logger = get_structured_logger(__name__, component="apm_integrations")


class NewRelicIntegration:
    """Integration with New Relic APM."""

    def __init__(self, license_key: str, app_name: str = "cidadao-ai"):
        self.license_key = license_key
        self.app_name = app_name
        self.base_url = "https://insights-collector.newrelic.com/v1/accounts"
        self.account_id = None  # Set this based on your New Relic account

        # Register handlers
        apm_hooks.register_error_handler(self.send_errors)
        apm_hooks.register_metric_handler(self.send_metrics)
        apm_hooks.register_event_handler(self.send_events)

    async def send_errors(self, errors: list[APMError]):
        """Send errors to New Relic."""
        if not self.account_id:
            logger.warning("New Relic account ID not configured")
            return

        events = []
        for error in errors:
            event = {
                "eventType": "CidadaoAIError",
                "timestamp": int(error.timestamp.timestamp()),
                "appName": self.app_name,
                "errorType": error.error_type,
                "errorMessage": error.message,
                "stackTrace": error.stack_trace,
                **error.tags,
                **error.context,
            }
            events.append(event)

        await self._send_to_newrelic(events, "events")

    async def send_metrics(self, metrics: list[APMPerformanceMetric]):
        """Send metrics to New Relic."""
        if not self.account_id:
            logger.warning("New Relic account ID not configured")
            return

        events = []
        for metric in metrics:
            event = {
                "eventType": "CidadaoAIMetric",
                "timestamp": int(metric.timestamp.timestamp()),
                "appName": self.app_name,
                "metricName": metric.metric_name,
                "value": metric.value,
                "unit": metric.unit,
                **metric.tags,
                **metric.dimensions,
            }
            events.append(event)

        await self._send_to_newrelic(events, "events")

    async def send_events(self, events: list[APMEvent]):
        """Send business events to New Relic."""
        if not self.account_id:
            logger.warning("New Relic account ID not configured")
            return

        nr_events = []
        for event in events:
            nr_event = {
                "eventType": f"CidadaoAI{event.event_type}",
                "timestamp": int(event.timestamp.timestamp()),
                "appName": self.app_name,
                **event.data,
                **event.tags,
                **event.metrics,
            }
            nr_events.append(nr_event)

        await self._send_to_newrelic(nr_events, "events")

    async def _send_to_newrelic(self, events: list[dict], endpoint: str):
        """Send data to New Relic."""
        try:
            url = f"{self.base_url}/{self.account_id}/{endpoint}"
            headers = {
                "Content-Type": "application/json",
                "X-License-Key": self.license_key,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, headers=headers, json=events, timeout=10.0
                )
                response.raise_for_status()

                logger.debug(
                    f"Sent {len(events)} events to New Relic",
                    operation="newrelic_send",
                    endpoint=endpoint,
                    events_count=len(events),
                )

        except Exception as e:
            logger.error(f"Failed to send data to New Relic: {e}")


class DatadogIntegration:
    """Integration with Datadog APM."""

    def __init__(self, api_key: str, app_key: str, site: str = "datadoghq.com"):
        self.api_key = api_key
        self.app_key = app_key
        self.site = site
        self.base_url = f"https://api.{site}/api/v1"

        # Register handlers
        apm_hooks.register_error_handler(self.send_errors)
        apm_hooks.register_metric_handler(self.send_metrics)
        apm_hooks.register_event_handler(self.send_events)

    async def send_errors(self, errors: list[APMError]):
        """Send errors to Datadog as logs."""
        logs = []
        for error in errors:
            log = {
                "timestamp": int(error.timestamp.timestamp() * 1000),
                "level": "error",
                "message": error.message,
                "service": "cidadao-ai",
                "source": "python",
                "tags": ",".join([f"{k}:{v}" for k, v in error.tags.items()]),
                "attributes": {
                    "error.type": error.error_type,
                    "error.stack": error.stack_trace,
                    **error.context,
                },
            }
            logs.append(log)

        await self._send_logs_to_datadog(logs)

    async def send_metrics(self, metrics: list[APMPerformanceMetric]):
        """Send metrics to Datadog."""
        series = []
        for metric in metrics:
            tags = [f"{k}:{v}" for k, v in metric.tags.items()]

            series_data = {
                "metric": f"cidadao_ai.{metric.metric_name}",
                "points": [[int(metric.timestamp.timestamp()), metric.value]],
                "tags": tags,
                "unit": metric.unit,
            }
            series.append(series_data)

        await self._send_metrics_to_datadog({"series": series})

    async def send_events(self, events: list[APMEvent]):
        """Send business events to Datadog."""
        for event in events:
            dd_event = {
                "title": f"Cidadão.AI {event.event_type}",
                "text": json_utils.dumps(event.data, indent=2),
                "date_happened": int(event.timestamp.timestamp()),
                "priority": "normal",
                "tags": [f"{k}:{v}" for k, v in event.tags.items()],
                "alert_type": "info",
                "source_type_name": "cidadao-ai",
            }

            await self._send_event_to_datadog(dd_event)

    async def _send_logs_to_datadog(self, logs: list[dict]):
        """Send logs to Datadog."""
        try:
            url = f"https://http-intake.logs.{self.site}/v1/input/{self.api_key}"
            headers = {"Content-Type": "application/json"}

            async with httpx.AsyncClient() as client:
                for log in logs:
                    response = await client.post(
                        url, headers=headers, json=log, timeout=10.0
                    )
                    response.raise_for_status()

        except Exception as e:
            logger.error(f"Failed to send logs to Datadog: {e}")

    async def _send_metrics_to_datadog(self, metrics_data: dict):
        """Send metrics to Datadog."""
        try:
            url = f"{self.base_url}/series"
            headers = {
                "Content-Type": "application/json",
                "DD-API-KEY": self.api_key,
                "DD-APPLICATION-KEY": self.app_key,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, headers=headers, json=metrics_data, timeout=10.0
                )
                response.raise_for_status()

        except Exception as e:
            logger.error(f"Failed to send metrics to Datadog: {e}")

    async def _send_event_to_datadog(self, event: dict):
        """Send event to Datadog."""
        try:
            url = f"{self.base_url}/events"
            headers = {
                "Content-Type": "application/json",
                "DD-API-KEY": self.api_key,
                "DD-APPLICATION-KEY": self.app_key,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, headers=headers, json=event, timeout=10.0
                )
                response.raise_for_status()

        except Exception as e:
            logger.error(f"Failed to send event to Datadog: {e}")


class ElasticAPMIntegration:
    """Integration with Elastic APM."""

    def __init__(
        self,
        server_url: str,
        secret_token: str | None = None,
        service_name: str = "cidadao-ai",
    ):
        self.server_url = server_url.rstrip("/")
        self.secret_token = secret_token
        self.service_name = service_name

        # Register handlers
        apm_hooks.register_error_handler(self.send_errors)
        apm_hooks.register_metric_handler(self.send_metrics)

    async def send_errors(self, errors: list[APMError]):
        """Send errors to Elastic APM."""
        for error in errors:
            error_data = {
                "service": {"name": self.service_name},
                "timestamp": int(error.timestamp.timestamp() * 1000000),  # microseconds
                "error": {
                    "exception": {
                        "message": error.message,
                        "type": error.error_type,
                        "stacktrace": [
                            {"filename": "unknown", "lineno": 0, "function": "unknown"}
                        ],
                    },
                    "context": {"tags": error.tags, "custom": error.context},
                },
            }

            await self._send_to_elastic(error_data, "errors")

    async def send_metrics(self, metrics: list[APMPerformanceMetric]):
        """Send metrics to Elastic APM."""
        metricsets = []
        for metric in metrics:
            metricset = {
                "service": {"name": self.service_name},
                "timestamp": int(metric.timestamp.timestamp() * 1000000),
                "metricset": {
                    "samples": {metric.metric_name: {"value": metric.value}},
                    "tags": metric.tags,
                },
            }
            metricsets.append(metricset)

        if metricsets:
            await self._send_to_elastic({"metricsets": metricsets}, "metrics")

    async def _send_to_elastic(self, data: dict, endpoint: str):
        """Send data to Elastic APM."""
        try:
            url = f"{self.server_url}/intake/v2/{endpoint}"
            headers = {"Content-Type": "application/x-ndjson"}

            if self.secret_token:
                headers["Authorization"] = f"Bearer {self.secret_token}"

            # Convert to NDJSON format
            ndjson_data = json_utils.dumps(data) + "\n"

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, headers=headers, content=ndjson_data, timeout=10.0
                )
                response.raise_for_status()

        except Exception as e:
            logger.error(f"Failed to send data to Elastic APM: {e}")


class APMIntegrations:
    """Manager for APM integrations."""

    def __init__(self):
        self.integrations: dict[str, Any] = {}
        self.enabled = False

    def setup_newrelic(
        self,
        license_key: str,
        app_name: str = "cidadao-ai",
        account_id: str | None = None,
    ):
        """Setup New Relic integration."""
        integration = NewRelicIntegration(license_key, app_name)
        if account_id:
            integration.account_id = account_id

        self.integrations["newrelic"] = integration

        logger.info("New Relic APM integration configured")

    def setup_datadog(self, api_key: str, app_key: str, site: str = "datadoghq.com"):
        """Setup Datadog integration."""
        integration = DatadogIntegration(api_key, app_key, site)
        self.integrations["datadog"] = integration

        logger.info("Datadog APM integration configured")

    def setup_elastic_apm(
        self,
        server_url: str,
        secret_token: str | None = None,
        service_name: str = "cidadao-ai",
    ):
        """Setup Elastic APM integration."""
        integration = ElasticAPMIntegration(server_url, secret_token, service_name)
        self.integrations["elastic"] = integration

        logger.info("Elastic APM integration configured")

    def enable_all(self):
        """Enable all configured integrations."""
        if self.integrations:
            apm_hooks.enable()
            self.enabled = True

            logger.info(
                f"Enabled {len(self.integrations)} APM integrations",
                integrations=list(self.integrations.keys()),
            )
        else:
            logger.warning("No APM integrations configured")

    def disable_all(self):
        """Disable all APM integrations."""
        apm_hooks.disable()
        self.enabled = False

        logger.info("Disabled all APM integrations")

    def get_status(self) -> dict[str, Any]:
        """Get status of all integrations."""
        return {
            "enabled": self.enabled,
            "integrations": list(self.integrations.keys()),
            "hooks_stats": apm_hooks.get_stats(),
        }


# Global APM integrations manager
apm_integrations = APMIntegrations()
