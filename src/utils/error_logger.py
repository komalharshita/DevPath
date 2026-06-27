# utils/error_logger.py
# Centralized error logging for DevPath.
#
# Responsibilities:
#   - Provide a single log_exception() function called by every error handler
#   - Sanitize error output so stack traces and sensitive data never reach
#     the HTTP response (they go to the server log only)
#   - Attach a short correlation ID to each event so log lines can be
#     matched across requests
#
# Usage:
#   from utils.error_logger import log_exception
#   log_exception(exc, status_code=500, context="optional extra info")

import logging
import traceback
import uuid
from typing import Optional

# ---------------------------------------------------------------------------
# Module-level logger
# ---------------------------------------------------------------------------
# In production Flask deployments the root logger is already configured by
# gunicorn / the WSGI host.  We create a named child logger so log records
# can be filtered / routed independently if needed.
# ---------------------------------------------------------------------------
logger = logging.getLogger("devpath.errors")

if not logger.handlers:
    # Provide a basic handler when running under pytest or the dev server so
    # that log lines actually appear without requiring external configuration.
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] %(levelname)s devpath.errors %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(_handler)
    logger.setLevel(logging.ERROR)


def log_exception(
    exc: Optional[BaseException],
    status_code: int = 500,
    context: str = "",
) -> str:
    """Log an exception securely and return a correlation ID.

    The full traceback is written to the server log only — it is never
    included in any HTTP response.  Callers receive a short correlation ID
    they can surface in the UI ("reference: <id>") so users can report
    issues without exposing internals.

    Args:
        exc:         The exception instance (may be None for synthetic errors).
        status_code: HTTP status code associated with this error.
        context:     Optional free-text label (e.g. the route name).

    Returns:
        A short alphanumeric correlation ID string.
    """
    correlation_id = uuid.uuid4().hex[:8]

    exc_type = type(exc).__name__ if exc is not None else "UnknownError"
    tb = (
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        if exc is not None
        else "No traceback available"
    )

    logger.error(
        "status=%d id=%s type=%s context=%r\n%s",
        status_code,
        correlation_id,
        exc_type,
        context or "—",
        tb,
    )

    return correlation_id
