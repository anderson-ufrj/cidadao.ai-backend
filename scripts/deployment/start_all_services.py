#!/usr/bin/env python3
"""
Multi-service startup script for Railway deployment.

This script starts all services (web, worker, beat) in a single process,
useful when you can't create multiple Railway services.

For production with multiple Railway services, use the Procfile directly.

Usage:
    python scripts/deployment/start_all_services.py

Author: Anderson H. Silva
Date: 2025-12-12
"""

import asyncio
import os
import signal
import subprocess
import sys
from datetime import datetime


class ServiceManager:
    """Manages multiple services in a single process."""

    def __init__(self):
        self.processes: dict[str, subprocess.Popen] = {}
        self.shutdown_requested = False
        self.port = os.getenv("PORT", "8000")

    def log(self, message: str, service: str = "manager"):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{service}] {message}", flush=True)

    def start_service(self, name: str, command: list[str]) -> subprocess.Popen:
        """Start a service and return its process."""
        self.log(f"Starting: {' '.join(command)}", name)

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        self.processes[name] = process
        return process

    async def stream_output(self, name: str, process: subprocess.Popen):
        """Stream output from a process."""
        try:
            while True:
                if process.poll() is not None:
                    # Process ended
                    break

                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        self.log(line.rstrip(), name)
                    else:
                        await asyncio.sleep(0.1)
                else:
                    await asyncio.sleep(0.1)
        except Exception as e:
            self.log(f"Error streaming output: {e}", name)

    def shutdown(self, signum=None, frame=None):
        """Shutdown all services gracefully."""
        if self.shutdown_requested:
            return

        self.shutdown_requested = True
        self.log("Shutting down all services...")

        for name, process in self.processes.items():
            if process.poll() is None:
                self.log(f"Stopping {name}...", name)
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.log(f"Force killing {name}...", name)
                    process.kill()

        self.log("All services stopped")

    async def run(self):
        """Start and manage all services."""
        # Register signal handlers
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)

        # Check Redis availability
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            self.log("WARNING: REDIS_URL not set. Celery services will fail.")
            self.log("Starting only the web service...")
            await self.run_web_only()
            return

        self.log("=" * 60)
        self.log("Starting Cidadão.AI Multi-Service Manager")
        self.log(f"PORT: {self.port}")
        self.log(f"REDIS: {redis_url[:30]}...")
        self.log("=" * 60)

        # Start Celery Beat (scheduler)
        beat_process = self.start_service(
            "beat",
            [
                "celery",
                "-A",
                "src.infrastructure.queue.celery_app",
                "beat",
                "--loglevel=info",
            ],
        )

        # Wait a bit for beat to start
        await asyncio.sleep(2)

        # Start Celery Worker
        worker_process = self.start_service(
            "worker",
            [
                "celery",
                "-A",
                "src.infrastructure.queue.celery_app",
                "worker",
                "--loglevel=info",
                "--queues=critical,high,default,low,background",
                "--concurrency=2",  # Reduced for single-service mode
            ],
        )

        # Wait a bit for worker to start
        await asyncio.sleep(2)

        # Start Web Server
        web_process = self.start_service(
            "web",
            [
                "uvicorn",
                "src.api.app:app",
                "--host",
                "0.0.0.0",
                "--port",
                self.port,
            ],
        )

        self.log("All services started!")
        self.log("=" * 60)

        # Stream output from all processes
        tasks = [
            asyncio.create_task(self.stream_output("beat", beat_process)),
            asyncio.create_task(self.stream_output("worker", worker_process)),
            asyncio.create_task(self.stream_output("web", web_process)),
        ]

        # Monitor processes
        while not self.shutdown_requested:
            for name, process in self.processes.items():
                if process.poll() is not None:
                    self.log(f"ALERT: {name} exited with code {process.returncode}")

                    # Restart critical services
                    if name == "web":
                        self.log("Web service died. Shutting down all services.")
                        self.shutdown()
                        break

            await asyncio.sleep(5)

        # Cancel streaming tasks
        for task in tasks:
            task.cancel()

    async def run_web_only(self):
        """Run only the web service (when Redis is not available)."""
        self.log("Running in web-only mode (no Celery)")

        web_process = self.start_service(
            "web",
            [
                "uvicorn",
                "src.api.app:app",
                "--host",
                "0.0.0.0",
                "--port",
                self.port,
            ],
        )

        # Stream output
        await self.stream_output("web", web_process)


def main():
    """Main entry point."""
    manager = ServiceManager()

    try:
        asyncio.run(manager.run())
    except KeyboardInterrupt:
        manager.shutdown()
    except Exception as e:
        print(f"Fatal error: {e}")
        manager.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    main()
