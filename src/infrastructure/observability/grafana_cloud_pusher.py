"""
Grafana Cloud Metrics Pusher

Sends Prometheus metrics to Grafana Cloud via Remote Write protocol.
Uses protobuf encoding and snappy compression as required by Grafana Cloud.

Author: Anderson Henrique da Silva
Location: Minas Gerais, Brasil
"""

import asyncio
import struct
import time
from contextlib import suppress

import httpx
import snappy
from prometheus_client import REGISTRY, generate_latest
from prometheus_client.parser import text_string_to_metric_families

from src.core import get_logger, settings

logger = get_logger(__name__)


class GrafanaCloudPusher:
    """Push metrics to Grafana Cloud via Remote Write protocol."""

    def __init__(self) -> None:
        self.url = settings.grafana_remote_write_url
        self.user = settings.grafana_remote_write_user
        self.token = (
            settings.grafana_remote_write_token.get_secret_value()
            if settings.grafana_remote_write_token
            else None
        )
        self.interval = settings.grafana_metrics_push_interval
        self._task: asyncio.Task | None = None
        self._running = False
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        """Check if Grafana Cloud is properly configured."""
        return bool(self.url and self.user and self.token)

    async def start(self) -> None:
        """Start periodic metrics push."""
        if not self.is_configured:
            logger.info(
                "grafana_cloud_push_disabled",
                reason="Missing GRAFANA_REMOTE_WRITE_URL, USER, or TOKEN",
            )
            return

        if self._running:
            logger.warning("grafana_cloud_pusher_already_running")
            return

        self._running = True
        self._client = httpx.AsyncClient(timeout=30.0)
        self._task = asyncio.create_task(self._push_loop())

        logger.info(
            "grafana_cloud_pusher_started",
            url=self.url,
            interval_seconds=self.interval,
        )

    async def stop(self) -> None:
        """Stop periodic metrics push."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

        if self._client:
            await self._client.aclose()
            self._client = None

        logger.info("grafana_cloud_pusher_stopped")

    async def _push_loop(self) -> None:
        """Background loop to push metrics periodically."""
        while self._running:
            try:
                await self._push_metrics()
            except Exception as e:
                logger.error("grafana_metrics_push_error", error=str(e))

            await asyncio.sleep(self.interval)

    async def _push_metrics(self) -> None:
        """Push current metrics to Grafana Cloud."""
        if not self._client:
            return

        try:
            # Generate metrics in Prometheus text format
            metrics_text = generate_latest(REGISTRY).decode("utf-8")

            # Convert to remote write format
            write_request = self._build_write_request(metrics_text)

            if not write_request["timeseries"]:
                return  # No metrics to push

            # Serialize to protobuf and compress with snappy
            payload = self._serialize_write_request(write_request)

            # Send to Grafana Cloud
            response = await self._client.post(
                self.url,
                content=payload,
                headers={
                    "Content-Type": "application/x-protobuf",
                    "Content-Encoding": "snappy",
                    "X-Prometheus-Remote-Write-Version": "0.1.0",
                },
                auth=(self.user, self.token),
            )

            if response.status_code in (200, 204):
                logger.debug(
                    "grafana_metrics_pushed",
                    timeseries_count=len(write_request["timeseries"]),
                )
            else:
                logger.warning(
                    "grafana_metrics_push_failed",
                    status_code=response.status_code,
                    response=response.text[:200],
                )

        except Exception as e:
            logger.error("grafana_metrics_push_exception", error=str(e))

    def _build_write_request(self, metrics_text: str) -> dict:
        """Convert Prometheus text format to remote write request."""
        timeseries = []
        timestamp_ms = int(time.time() * 1000)

        for family in text_string_to_metric_families(metrics_text):
            for sample in family.samples:
                # Build labels
                labels = [{"name": "__name__", "value": sample.name}]
                for label_name, label_value in sample.labels.items():
                    labels.append({"name": label_name, "value": str(label_value)})

                # Add job and instance labels for identification
                labels.append({"name": "job", "value": "cidadao-ai-backend"})
                labels.append({"name": "instance", "value": "railway-production"})

                # Build timeseries
                timeseries.append(
                    {
                        "labels": labels,
                        "samples": [{"value": sample.value, "timestamp": timestamp_ms}],
                    }
                )

        return {"timeseries": timeseries}

    def _serialize_write_request(self, write_request: dict) -> bytes:
        """Serialize write request to protobuf and compress with snappy."""
        data = self._encode_write_request(write_request)
        return snappy.compress(data)

    def _encode_write_request(self, write_request: dict) -> bytes:
        """Encode write request to protobuf wire format."""
        # Protobuf encoding for WriteRequest
        # Message WriteRequest { repeated TimeSeries timeseries = 1; }
        result = b""

        for ts in write_request["timeseries"]:
            ts_bytes = self._encode_timeseries(ts)
            # Field 1, wire type 2 (length-delimited)
            result += b"\x0a" + self._encode_varint(len(ts_bytes)) + ts_bytes

        return result

    def _encode_timeseries(self, ts: dict) -> bytes:
        """Encode a single TimeSeries to protobuf."""
        result = b""

        # Labels (field 1, repeated)
        for label in ts["labels"]:
            label_bytes = self._encode_label(label)
            result += b"\x0a" + self._encode_varint(len(label_bytes)) + label_bytes

        # Samples (field 2, repeated)
        for sample in ts["samples"]:
            sample_bytes = self._encode_sample(sample)
            result += b"\x12" + self._encode_varint(len(sample_bytes)) + sample_bytes

        return result

    def _encode_label(self, label: dict) -> bytes:
        """Encode a Label to protobuf."""
        result = b""
        # name (field 1, string)
        name_bytes = label["name"].encode("utf-8")
        result += b"\x0a" + self._encode_varint(len(name_bytes)) + name_bytes
        # value (field 2, string)
        value_bytes = label["value"].encode("utf-8")
        result += b"\x12" + self._encode_varint(len(value_bytes)) + value_bytes
        return result

    def _encode_sample(self, sample: dict) -> bytes:
        """Encode a Sample to protobuf."""
        result = b""
        # value (field 1, double)
        result += b"\x09" + struct.pack("<d", sample["value"])
        # timestamp (field 2, int64)
        result += b"\x10" + self._encode_varint(sample["timestamp"])
        return result

    def _encode_varint(self, value: int) -> bytes:
        """Encode an integer as a protobuf varint."""
        result = b""
        while value > 127:
            result += bytes([(value & 0x7F) | 0x80])
            value >>= 7
        result += bytes([value & 0x7F])
        return result


# Global instance
grafana_pusher = GrafanaCloudPusher()
