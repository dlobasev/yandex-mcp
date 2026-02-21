"""Constants and configuration for Yandex MCP Server."""

# API Endpoints
YANDEX_DIRECT_API_URL = "https://api.direct.yandex.com/json/v5"
YANDEX_DIRECT_API_URL_V501 = "https://api.direct.yandex.com/json/v501"
YANDEX_DIRECT_SANDBOX_URL = "https://api-sandbox.direct.yandex.com/json/v5"
YANDEX_METRIKA_API_URL = "https://api-metrika.yandex.net"
YANDEX_WORDSTAT_API_URL = "https://api.wordstat.yandex.net"

# Timeouts (seconds)
DEFAULT_TIMEOUT = 30.0
REPORTS_TIMEOUT = 120.0

# Monetary conversion
MICROS_MULTIPLIER = 1_000_000

# Row limits for markdown formatting
METRIKA_REPORT_MAX_ROWS = 50
DIRECT_REPORT_MAX_ROWS = 100
METRIKA_COUNTER_GOALS_PREVIEW_LIMIT = 10

# AdImage limits
AD_IMAGE_MAX_PER_REQUEST = 3
