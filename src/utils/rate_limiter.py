# utils/rate_limiter.py
# Lightweight, dependency-free rate limiting for DevPath.
#
# Tracks request timestamps per (client IP, route) in a sliding window, using
# only a module-level dict (no flask-limiter/Redis, keeping Flask as the only
# runtime dependency). When a client exceeds the limit, it raises
# werkzeug's TooManyRequests, which Flask routes to the existing 429
# handler in errors/handlers.py — so this module just decides allow/deny
# and leaves response-building to the code that already does it. Note
# this is single-process only: running multiple workers means each one
# tracks its own counters.

import time
from collections import defaultdict
from functools import wraps

from flask import request
from werkzeug.exceptions import TooManyRequests

# (client_id, endpoint) -> list[float] of request timestamps in the window.
_request_log = defaultdict(list)


def _client_identifier() -> str:
    """Identify the caller for rate-limiting purposes (by IP)."""
    return request.remote_addr or "unknown"


def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """Decorator: limit a view to `max_requests` per `window_seconds`."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            # Keyed by (client, endpoint) so one route's traffic can't
            # consume another route's budget for the same client.
            key = (_client_identifier(), request.endpoint)
            now = time.time()
            window_start = now - window_seconds

            timestamps = _request_log[key]
            # Drop timestamps outside the current window.
            timestamps[:] = [t for t in timestamps if t > window_start]

            if len(timestamps) >= max_requests:
                raise TooManyRequests(
                    description="Rate limit exceeded. Please slow down."
                )

            timestamps.append(now)
            return view_func(*args, **kwargs)

        return wrapped

    return decorator


def reset_rate_limits() -> None:
    """Clear all tracked timestamps (for use between tests)."""
    _request_log.clear()