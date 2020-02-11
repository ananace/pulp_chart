"""
Check `Plugin Writer's Guide`_ for more details.

.. _Plugin Writer's Guide:
    http://docs.pulpproject.org/en/3.0/nightly/plugins/plugin-writer/index.html
"""

from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from pulpcore.app.viewsets import RemoteFilter
from pulpcore.plugin import viewsets as core
from pulpcore.plugin.actions import ModifyRepositoryActionMixin
from pulpcore.plugin.serializers import (
    AsyncOperationResponseSerializer,
    RepositorySyncURLSerializer,
)
from pulpcore.plugin.tasking import enqueue_with_reservation
from pulpcore.plugin.models import ContentArtifact

from . import models, serializers, tasks


class ChartContentFilter(core.ContentFilter):
    """
    FilterSet for ChartContent.
    """

    class Meta:
        model = models.ChartContent
        fields = [
            # ...
        ]


class ChartContentViewSet(core.SingleArtifactContentUploadViewSet):
    """
    A ViewSet for ChartContent.
    """

    endpoint_name = "chart"
    queryset = models.ChartContent.objects.all()
    serializer_class = serializers.ChartContentSerializer
    filterset_class = ChartContentFilter

    @transaction.atomic
    def create(self, request):
        """
        Perform bookkeeping when saving Content.

        "Artifacts" need to be popped off and saved indpendently, as they are not actually part
        of the Content model.
        """
        raise NotImplementedError("FIXME")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        _artifact = serializer.validated_data.pop("_artifact")
        content = serializer.save()

        if content.pk:
           ContentArtifact.objects.create(
               artifact=artifact,
               content=content,
               relative_path=
           )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ChartRemoteFilter(RemoteFilter):
    """
    A FilterSet for ChartRemote.
    """

    class Meta:
        model = models.ChartRemote
        fields = [
            # ...
        ]


class ChartRemoteViewSet(core.RemoteViewSet):
    """
    A ViewSet for ChartRemote.
    """

    endpoint_name = "chart"
    queryset = models.ChartRemote.objects.all()
    serializer_class = serializers.ChartRemoteSerializer


class ChartRepositoryViewSet(core.RepositoryViewSet, ModifyRepositoryActionMixin):
    """
    A ViewSet for ChartRepository.
    """

    endpoint_name = "chart"
    queryset = models.ChartRepository.objects.all()
    serializer_class = serializers.ChartRepositorySerializer

    # This decorator is necessary since a sync operation is asyncrounous and returns
    # the id and href of the sync task.
    @swagger_auto_schema(
        operation_description="Trigger an asynchronous task to sync content.",
        operation_summary="Sync from remote",
        responses={202: AsyncOperationResponseSerializer},
    )
    @action(detail=True, methods=["post"], serializer_class=RepositorySyncURLSerializer)
    def sync(self, request, pk):
        """
        Dispatches a sync task.
        """
        repository = self.get_object()
        serializer = RepositorySyncURLSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        remote = serializer.validated_data.get("remote")
        mirror = serializer.validated_data.get('mirror')

        result = enqueue_with_reservation(
            tasks.synchronize,
            [repository, remote],
            kwargs={
                "remote_pk": remote.pk,
                "repository_pk": repository.pk,
                "mirror": mirror
            },
        )
        return core.OperationPostponedResponse(result, request)


class ChartRepositoryVersionViewSet(core.RepositoryVersionViewSet):
    """
    A ViewSet for a ChartRepositoryVersion represents a single
    Chart repository version.
    """

    parent_viewset = ChartRepositoryViewSet


class ChartPublicationViewSet(core.PublicationViewSet):
    """
    A ViewSet for ChartPublication.
    """

    endpoint_name = "chart"
    queryset = models.ChartPublication.objects.all()
    serializer_class = serializers.ChartPublicationSerializer

    # This decorator is necessary since a publish operation is asyncrounous and returns
    # the id and href of the publish task.
    @swagger_auto_schema(
        operation_description="Trigger an asynchronous task to publish content",
        responses={202: AsyncOperationResponseSerializer},
    )
    def create(self, request):
        """
        Publishes a repository.

        Either the ``repository`` or the ``repository_version`` fields can
        be provided but not both at the same time.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        repository_version = serializer.validated_data.get("repository_version")

        result = enqueue_with_reservation(
            tasks.publish,
            [repository_version.repository],
            kwargs={"repository_version_pk": str(repository_version.pk),},
        )
        return core.OperationPostponedResponse(result, request)


class ChartDistributionViewSet(core.BaseDistributionViewSet):
    """
    A ViewSet for ChartDistribution.
    """

    endpoint_name = "chart"
    queryset = models.ChartDistribution.objects.all()
    serializer_class = serializers.ChartDistributionSerializer
