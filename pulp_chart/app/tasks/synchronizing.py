from gettext import gettext as _
import logging
from urllib.parse import urljoin
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
        remote_url = self.remote.url
        if not remote_url.endswith('/index.yaml'):
            remote_url += '/index.yaml'

        index_yaml = []
        with ProgressReport(message="Downloading Index", code="downloading.metadata") as pb:
            downloader = self.remote.get_downloader(url=remote_url)
            result = await downloader.run()
            index_yaml = list(self.read_index_yaml(result.path))
            pb.increment()

        with ProgressReport(message="Parsing Entries", code="parsing.metadata") as pb:
            pb.total = len(index_yaml)
            pb.save()

            for entry in index_yaml:
                content_entry = dict(filter(lambda e:e[0] not in ('url'), entry.items()))

                unit = ChartContent(**content_entry)
                artifact = Artifact(sha256=entry['digest'])

                da = DeclarativeArtifact(
                    artifact,
                    urljoin(remote_url, entry['url']),
                    "{}-{}.tgz".format(entry['name'], entry['version']),
                    self.remote,
                    deferred_download=self.deferred_download,
                )
                dc = DeclarativeContent(content=unit, d_artifacts=[da])
                pb.increment()
                await self.put(dc)

    def read_index_yaml(self, path):
        """
        Parse the metadata for chart Content type.

        Args:
            path: Path to the metadata file
        """
        doc = yaml.load(open(path), loader=yaml.SafeLoader)

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

