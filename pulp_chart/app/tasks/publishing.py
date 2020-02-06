import logging
import os
import yaml
from gettext import gettext as _

from django.core.files import File
from django.utils import timezone

from pulpcore.plugin.models import (
    RepositoryVersion,
    PublishedArtifact,
    PublishedMetadata,
    RemoteArtifact,
)
from pulpcore.plugin.tasking import WorkingDirectory

from pulp_chart.app.models import (
    ChartContent,
    ChartPublication
)


log = logging.getLogger(__name__)


def publish(repository_version_pk):
    """
    Create a Publication based on a RepositoryVersion.

    Args:
        repository_version_pk (str): Create a publication from this repository version.
    """
    repository_version = RepositoryVersion.objects.get(pk=repository_version_pk)

    log.info(
        _("Publishing: repository={repo}, version={ver}").format(
            repo=repository_version.repository.name, ver=repository_version.number,
        )
    )
    with WorkingDirectory():
        with ChartPublication.create(repository_version) as publication:
            publish_chart_content(publication)

    log.info(_("Publication: {publication} created").format(publication=publication.pk))


def publish_chart_content(publication):
    """
    Create published artifacts and metadata for a publication

    Args:
        publication (ChartPublication): The publication to store
    """
    entries = {}
    for content in ChartContent.objects.filter(
        pk__in=publication.repository_version.content
    ).order_by('name','-created'):
        artifacts = content.contentartifact_set.all()
        for artifact in artifacts:
            published = PublishedArtifact(
                relative_path=artifact.relative_path,
                publication=publication,
                content_artifact=artifact
            )
            published.save()

        entry = {
            'apiVersion': 'v1',
            'created': content.created.isoformat(),
            'description': content.description,
            'digest': content.digest,
            'icon': content.icon,
            'keywords': content.keywords,
            'name': content.name,
            'urls': [artifact.relative_path for artifact in artifacts],
            'version': content.version
        }

        if content.name not in entries:
            entries[content.name] = []

        # Strip away empty keys when building metadata
        entries[content.name].append(
            {k: v for k, v in entry.items() if (v is not None and v != []) }
        )

    doc = {
        'apiVersion': 'v1',
        'entries': entries,
        'generated': timezone.now().isoformat()
    }

    with open('index.yaml', 'w') as index:
        index.write(yaml.dump(doc))

    index = PublishedMetadata.create_from_file(
        publication=publication,
        file=File(open('index.yaml', 'rb'))
    )
    index.save()
