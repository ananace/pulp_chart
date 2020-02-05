# coding=utf-8
"""Constants for Pulp Chart plugin tests."""
from urllib.parse import urljoin

from pulp_smash.constants import PULP_FIXTURES_BASE_URL
from pulp_smash.pulp3.constants import (
    BASE_DISTRIBUTION_PATH,
    BASE_PUBLICATION_PATH,
    BASE_REMOTE_PATH,
    BASE_REPO_PATH,
    BASE_CONTENT_PATH,
)

# FIXME: list any download policies supported by your plugin type here.
# If your plugin supports all download policies, you can import this
# from pulp_smash.pulp3.constants instead.
# DOWNLOAD_POLICIES = ["immediate", "streamed", "on_demand"]
DOWNLOAD_POLICIES = ["immediate"]

# FIXME: replace 'unit' with your own content type names, and duplicate as necessary for each type
CHART_CONTENT_NAME = "chart.unit"

# FIXME: replace 'unit' with your own content type names, and duplicate as necessary for each type
CHART_CONTENT_PATH = urljoin(BASE_CONTENT_PATH, "chart/units/")

CHART_REMOTE_PATH = urljoin(BASE_REMOTE_PATH, "chart/chart/")

CHART_REPO_PATH = urljoin(BASE_REPO_PATH, "chart/chart/")

CHART_PUBLICATION_PATH = urljoin(BASE_PUBLICATION_PATH, "chart/chart/")

CHART_DISTRIBUTION_PATH = urljoin(BASE_DISTRIBUTION_PATH, "chart/chart/")

# FIXME: replace this with your own fixture repository URL and metadata
CHART_FIXTURE_URL = urljoin(PULP_FIXTURES_BASE_URL, "chart/")
"""The URL to a chart repository."""

# FIXME: replace this with the actual number of content units in your test fixture
CHART_FIXTURE_COUNT = 3
"""The number of content units available at :data:`CHART_FIXTURE_URL`."""

CHART_FIXTURE_SUMMARY = {CHART_CONTENT_NAME: CHART_FIXTURE_COUNT}
"""The desired content summary after syncing :data:`CHART_FIXTURE_URL`."""

# FIXME: replace this with the location of one specific content unit of your choosing
CHART_URL = urljoin(CHART_FIXTURE_URL, "")
"""The URL to an chart file at :data:`CHART_FIXTURE_URL`."""

# FIXME: replace this with your own fixture repository URL and metadata
CHART_INVALID_FIXTURE_URL = urljoin(PULP_FIXTURES_BASE_URL, "chart-invalid/")
"""The URL to an invalid chart repository."""

# FIXME: replace this with your own fixture repository URL and metadata
CHART_LARGE_FIXTURE_URL = urljoin(PULP_FIXTURES_BASE_URL, "chart_large/")
"""The URL to a chart repository containing a large number of content units."""

# FIXME: replace this with the actual number of content units in your test fixture
CHART_LARGE_FIXTURE_COUNT = 25
"""The number of content units available at :data:`CHART_LARGE_FIXTURE_URL`."""
