"""
Minimal JSON-based logging utilities for MCP server.

Provides structured logging for tools, resources, and errors.
"""
import logging
import json
import time
from functools import wraps
from typing import Callable


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs JSON-structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


def setup_logger(name: str = "mcp_server") -> logging.Logger:
    """Set up JSON logger for MCP server."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler with JSON formatting
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    return logger


# Global logger instance
logger = setup_logger()


def log_tool_call(func: Callable) -> Callable:
    """Decorator to log tool execution metrics."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        tool_name = func.__name__
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000

            # Calculate result size
            result_count = len(result) if isinstance(result, list) else 1

            # Log success
            logger.info(
                "Tool execution completed",
                extra={
                    "extra_fields": {
                        "event_type": "tool_call",
                        "tool_name": tool_name,
                        "duration_ms": round(duration_ms, 2),
                        "result_count": result_count,
                        "status": "success",
                    }
                },
            )

            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            logger.error(
                f"Tool execution failed: {str(e)}",
                extra={
                    "extra_fields": {
                        "event_type": "tool_call",
                        "tool_name": tool_name,
                        "duration_ms": round(duration_ms, 2),
                        "status": "error",
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    }
                },
            )
            raise

    return wrapper


def log_resource_access(func: Callable) -> Callable:
    """Decorator to log resource access metrics."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        resource_name = func.__name__
        start_time = time.time()

        # Extract URL from arguments
        url = kwargs.get("url") or (args[0] if args else "unknown")

        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000

            # Calculate result size
            result_size = len(result) if isinstance(result, str) else 0

            # Log success
            logger.info(
                "Resource access completed",
                extra={
                    "extra_fields": {
                        "event_type": "resource_access",
                        "resource_name": resource_name,
                        "url": url,
                        "duration_ms": round(duration_ms, 2),
                        "result_size_chars": result_size,
                        "status": "success",
                    }
                },
            )

            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            logger.error(
                f"Resource access failed: {str(e)}",
                extra={
                    "extra_fields": {
                        "event_type": "resource_access",
                        "resource_name": resource_name,
                        "url": url,
                        "duration_ms": round(duration_ms, 2),
                        "status": "error",
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    }
                },
            )
            raise

    return wrapper


def log_server_start(product: str, transport: str):
    """Log server startup."""
    logger.info(
        "MCP server starting",
        extra={
            "extra_fields": {
                "event_type": "server_start",
                "product": product,
                "transport": transport,
            }
        },
    )


def log_server_ready(product: str, transport: str, port: int = None):
    """Log server ready state."""
    extra_fields = {
        "event_type": "server_ready",
        "product": product,
        "transport": transport,
    }

    if port:
        extra_fields["port"] = port

    logger.info("MCP server ready", extra={"extra_fields": extra_fields})
