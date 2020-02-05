from gettext import gettext as _
import logging
import yaml

from pulpcore.plugin.models import Artifact, ProgressReport, Remote, Repository
from pulpcore.plugin.stages import (
    DeclarativeArtifact,
    DeclarativeContent,
    DeclarativeVersion,
    Stage,
)

from pulp_chart.app.models import ChartContent, ChartRemote


log = logging.getLogger(__name__)


def synchronize(remote_pk, repository_pk):# , mirror):
    """
    Sync content from the remote repository.

    Create a new version of the repository that is synchronized with the remote.

    Args:
        remote_pk (str): The remote PK.
        repository_pk (str): The repository PK.
        mirror (bool): True for mirror mode, False for additive.

    Raises:
        ValueError: If the remote does not specify a URL to sync

    """
    remote = ChartRemote.objects.get(pk=remote_pk)
    repository = Repository.objects.get(pk=repository_pk)

    if not remote.url:
        raise ValueError(_("A remote must have a url specified to synchronize."))

    # Interpret policy to download Artifacts or not
    deferred_download = remote.policy != Remote.IMMEDIATE
    first_stage = ChartFirstStage(remote, deferred_download)
    DeclarativeVersion(first_stage, repository, mirror=False).create()


class ChartFirstStage(Stage):
    """
    The first stage of a pulp_chart sync pipeline.
    """

    def __init__(self, remote, deferred_download):
        """
        The first stage of a pulp_chart sync pipeline.

        Args:
            remote (FileRemote): The remote data to be used when syncing
            deferred_download (bool): if True the downloading will not happen now. If False, it will
                happen immediately.

        """
        super().__init__()
        self.remote = remote
        self.deferred_download = deferred_download

    async def run(self):
        """
        Build and emit `DeclarativeContent` from the Manifest data.

        Args:
            in_q (asyncio.Queue): Unused because the first stage doesn't read from an input queue.
            out_q (asyncio.Queue): The out_q to send `DeclarativeContent` objects to

        """
        downloader = self.remote.get_downloader(url=self.remote.url)
        result = await downloader.run()
        # Use ProgressReport to report progress
        for entry in self.read_index_yaml(result.path):
            content_entry = dict(filter(lambda e:e[0] not in ('url'), entry.items()))

            unit = ChartContent(**content_entry)
            artifact = Artifact(sha256=entry['digest'])

            da = DeclarativeArtifact(
                artifact,
                entry['url'],
                "{}-{}.tgz".format(entry['name'], entry['version']),
                self.remote,
                deferred_download=self.deferred_download,
            )
            dc = DeclarativeContent(content=unit, d_artifacts=[da])
            await self.put(dc)

    def read_index_yaml(self, path):
        """
        Parse the metadata for chart Content type.

        Args:
            path: Path to the metadata file
        """
        doc = yaml.load(open(path))

        for name, versions in doc['entries'].items():
            for version in versions:
                data = {
                    'name': version['name'],
                    'version': version['version'],
                    'digest': version['digest'],

                    'url': version['urls'][0],

                    'created': version.get('created'),
                    'app_version': version.get('appVersion'),
                    'description': version.get('description'),
                    'icon': version.get('icon'),
                    'keywords': version.get('keywords', [])
                }
                yield data

