import os
import tarfile
import tempfile
import yaml

from pulpcore.plugin.models import Artifact, CreatedResource
from rest_framework import serializers

from pulp_chart.app.models import ChartContent, ChartRepository


def one_shot_upload(artifact_pk, filename, repository_pk=None):
    """
    One shot upload for pulp_python
    Args:
        artifact_pk: validated artifact
        filename: file name
        repository_pk: optional repository to add Content to
    """

    chart={}
    with tempfile.TemporaryDirectory() as td:
        temp_path = os.path.join(td, filename)
        artifact = Artifact.objects.get(pk=artifact_pk)
        shutil.copy2(artifact.file.path, temp_path)

        with tarfile.open(temp_path) as tarball:
            chart_member = [m for m in tf.getmembers() if m.name.endswith('Chart.yaml') and m.name.count('/') == 1]
            if len(chart_member) != 1:
                 raise serializers.ValidationError('Unable to find Chart.yaml')

            chart_file = tarball.extractfile(chart_member)
            doc = yaml.load(chart_file, loader=yaml.SafeLoader)
            chart = {
                'name': doc['name'],
                'version': doc['version'],
                'digest': doc['digest'],

                # TODO: Handle multiple URLs better, maybe failover?
                'url': doc['urls'][0],

                'created': doc.get('created'),
                'app_version': doc.get('appVersion'),
                'description': doc.get('description'),
                'icon': doc.get('icon'),
                'keywords': doc.get('keywords', [])
            }


    new_content = ChartContent(**chart)
    new_content.save()

    if repository_pk:
        queryset = ChartContent.objects.filter(pk=new_content.pk)
        repository = ChartRepository.objects.get(pk=repository_pk)
        with repository.new_version() as new_version:
            new_version.add_content(queryset)

    resource = CreatedResource(content_object=new_content)
    resource.save()
