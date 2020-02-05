# coding=utf-8
"""Utilities for tests for the chart plugin."""
from functools import partial
import requests
from unittest import SkipTest
from time import sleep
from tempfile import NamedTemporaryFile

from pulp_smash import api, selectors
from pulp_smash.pulp3.utils import (
    gen_remote,
    gen_repo,
    get_content,
    require_pulp_3,
    require_pulp_plugins,
    sync,
)

from pulp_chart.tests.functional.constants import (
    CHART_CONTENT_NAME,
    CHART_CONTENT_PATH,
    CHART_FIXTURE_URL,
    CHART_PUBLICATION_PATH,
    CHART_REMOTE_PATH,
    CHART_REPO_PATH,
    CHART_URL,
)

from pulpcore.client.pulpcore import (
    ApiClient as CoreApiClient,
    ArtifactsApi,
    Configuration,
    TasksApi,
)
from pulpcore.client.pulp_chart import ApiClient as ChartApiClient


configuration = Configuration()
configuration.username = "admin"
configuration.password = "password"
configuration.safe_chars_for_path_param = "/"


def set_up_module():
    """Skip tests Pulp 3 isn't under test or if pulp_chart isn't installed."""
    require_pulp_3(SkipTest)
    require_pulp_plugins({"pulp_chart"}, SkipTest)


def gen_chart_client():
    """Return an OBJECT for chart client."""
    return ChartApiClient(configuration)


def gen_chart_remote(url=CHART_FIXTURE_URL, **kwargs):
    """Return a semi-random dict for use in creating a chart Remote.

    :param url: The URL of an external content source.
    """
    # FIXME: Add any fields specific to a chart remote here
    return gen_remote(url, **kwargs)


def get_chart_content_paths(repo, version_href=None):
    """Return the relative path of content units present in a chart repository.

    :param repo: A dict of information about the repository.
    :param version_href: The repository version to read.
    :returns: A dict of lists with the paths of units present in a given repository.
        Paths are given as pairs with the remote and the local version for different content types.
    """
    # FIXME: The "relative_path" is actually a file path and name
    # It's just an example -- this needs to be replaced with an implementation that works
    # for repositories of this content type.
    return {
        CHART_CONTENT_NAME: [
            (content_unit["relative_path"], content_unit["relative_path"])
            for content_unit in get_content(repo, version_href)[CHART_CONTENT_NAME]
        ],
    }


def gen_chart_content_attrs(artifact):
    """Generate a dict with content unit attributes.

    :param artifact: A dict of info about the artifact.
    :returns: A semi-random dict for use in creating a content unit.
    """
    # FIXME: Add content specific metadata here.
    return {"_artifact": artifact["pulp_href"]}


def populate_pulp(cfg, url=CHART_FIXTURE_URL):
    """Add chart contents to Pulp.

    :param pulp_smash.config.PulpSmashConfig: Information about a Pulp application.
    :param url: The chart repository URL. Defaults to
        :data:`pulp_smash.constants.CHART_FIXTURE_URL`
    :returns: A list of dicts, where each dict describes one chart content in Pulp.
    """
    client = api.Client(cfg, api.json_handler)
    remote = {}
    repo = {}
    try:
        remote.update(client.post(CHART_REMOTE_PATH, gen_chart_remote(url)))
        repo.update(client.post(CHART_REPO_PATH, gen_repo()))
        sync(cfg, remote, repo)
    finally:
        if remote:
            client.delete(remote["pulp_href"])
        if repo:
            client.delete(repo["pulp_href"])
    return client.get(CHART_CONTENT_PATH)["results"]


def publish(cfg, repo, version_href=None):
    """Publish a repository.
    :param pulp_smash.config.PulpSmashConfig cfg: Information about the Pulp
        host.
    :param repo: A dict of information about the repository.
    :param version_href: A href for the repo version to be published.
    :returns: A publication. A dict of information about the just created
        publication.
    """
    if version_href:
        body = {"repository_version": version_href}
    else:
        body = {"repository": repo["pulp_href"]}

    client = api.Client(cfg, api.json_handler)
    call_report = client.post(CHART_PUBLICATION_PATH, body)
    tasks = tuple(api.poll_spawned_tasks(cfg, call_report))
    return client.get(tasks[-1]["created_resources"][0])


skip_if = partial(selectors.skip_if, exc=SkipTest)  # pylint:disable=invalid-name
"""The ``@skip_if`` decorator, customized for unittest.

:func:`pulp_smash.selectors.skip_if` is test runner agnostic. This function is
identical, except that ``exc`` has been set to ``unittest.SkipTest``.
"""

core_client = CoreApiClient(configuration)
tasks = TasksApi(core_client)


def gen_artifact(url=CHART_URL):
    """Creates an artifact."""
    response = requests.get(url)
    with NamedTemporaryFile() as temp_file:
        temp_file.write(response.content)
        artifact = ArtifactsApi(core_client).create(file=temp_file.name)
        return artifact.to_dict()


def monitor_task(task_href):
    """Polls the Task API until the task is in a completed state.

    Prints the task details and a success or failure message. Exits on failure.

    Args:
        task_href(str): The href of the task to monitor

    Returns:
        list[str]: List of hrefs that identify resource created by the task

    """
    completed = ["completed", "failed", "canceled"]
    task = tasks.read(task_href)
    while task.state not in completed:
        sleep(2)
        task = tasks.read(task_href)

    if task.state == "completed":
        return task.created_resources

    return task.to_dict()
