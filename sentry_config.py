import logging
import os
import sentry_sdk
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


def init_sentry():
    """Initialize Sentry SDK with proper configuration."""
    sentry_dsn = os.getenv("SENTRY_DSN")
    if not sentry_dsn:
        logging.warning(
            "SENTRY_DSN environment variable not set. Skipping Sentry initialization."
        )
        return

    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[
            HttpxIntegration(),  # Capture HTTP requests
            LoggingIntegration(
                level=logging.INFO,  # Capture INFO+ as breadcrumbs
                event_level=logging.CRITICAL,  # Only send CRITICAL+ as Issues (effectively disables Issues)
            ),
        ],
        send_default_pii=True,
        environment=os.getenv("ENVIRONMENT", "development"),
        enable_logs=True,
    )
