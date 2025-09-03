import logging
import os
import sentry_sdk
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


def init_sentry():
    """Initialize Sentry SDK with proper configuration."""
    sentry_sdk.init(
        dsn="https://5f012080e6c7495038a9ba8a1e7ea2ff@o4504294971801600.ingest.us.sentry.io/4509957539758081",
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
