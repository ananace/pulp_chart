"""
Check `Plugin Writer's Guide`_ for more details.

.. _Plugin Writer's Guide:
    http://docs.pulpproject.org/en/3.0/nightly/plugins/plugin-writer/index.html
"""

from logging import getLogger

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from pulpcore.plugin.models import (
    Content,
    ContentArtifact,
    Remote,
    Repository,
    Publication,
    PublicationDistribution,
)

logger = getLogger(__name__)


class ChartContent(Content):
    """
    The "chart" content type.

    Define fields you need for your new content type and
    specify uniqueness constraint to identify unit of this type.

    For example::

        field1 = models.TextField()
        field2 = models.IntegerField()
        field3 = models.CharField()

        class Meta:
            default_related_name = "%(app_label)s_%(model_name)s"
            unique_together = (field1, field2)
    """

    # Required chart metadata
    name = models.TextField(null=False)
    version = models.TextField(null=False)
    digest = models.CharField(null=False, max_length=64) # SHA256 digest

    created = models.DateTimeField(default=timezone.now)

    # Optional chart metadata
    app_version = models.TextField(null=True)
    description = models.TextField(null=True)
    icon = models.TextField(null=True)

    keywords = ArrayField(
        models.TextField(null=False),
        null=True
    )

    TYPE = "chart"

    class Meta:
        default_related_name = "%(app_label)s_%(model_name)s"
        unique_together = ('name', 'version', 'digest')


class ChartPublication(Publication):
    """
    A Publication for ChartContent.

    Define any additional fields for your new publication if needed.
    """

    TYPE = "chart"

    class Meta:
        default_related_name = "%(app_label)s_%(model_name)s"


class ChartRemote(Remote):
    """
    A Remote for ChartContent.

    Define any additional fields for your new remote if needed.
    """

    TYPE = "chart"

    class Meta:
        default_related_name = "%(app_label)s_%(model_name)s"


class ChartRepository(Repository):
    """
    A Repository for ChartContent.

    Define any additional fields for your new repository if needed.
    """

    TYPE = "chart"

    CONTENT_TYPES = [ChartContent]

    class Meta:
        default_related_name = "%(app_label)s_%(model_name)s"


class ChartDistribution(PublicationDistribution):
    """
    A Distribution for ChartContent.

    Define any additional fields for your new distribution if needed.
    """

    TYPE = "chart"

    class Meta:
        default_related_name = "%(app_label)s_%(model_name)s"
