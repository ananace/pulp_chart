from pulpcore.plugin import PulpPluginAppConfig


class PulpChartPluginAppConfig(PulpPluginAppConfig):
    """Entry point for the chart plugin."""

    name = "pulp_chart.app"
    label = "chart"
