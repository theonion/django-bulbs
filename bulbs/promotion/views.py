import json

from dateutil.parser import parse as parse_date

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.http import Http404
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from bulbs.api.permissions import CanPromoteContent
from bulbs.api.mixins import UncachedResponse

from bulbs.utils.methods import get_query_params

from .models import PZone
from .operations import PZoneOperation, InsertOperation, DeleteOperation, ReplaceOperation
from .serializers import PZoneSerializer, InsertOperationSerializer, DeleteOperationSerializer, ReplaceOperationSerializer


class OperationsViewSet(APIView):

    permission_classes = [IsAdminUser, CanPromoteContent]

    def get_serializer_class_by_name(self, type_name):
        try:
            # try to convert type name into a serializer class
            app_label, model_name = type_name.split("_")
            operation_type = ContentType.objects.get_by_natural_key(app_label, model_name)
            operation_model = operation_type.model_class()
            return self.get_serializer_class(operation_model)
        except (ValueError, ContentType.DoesNotExist):
            # invalid type name
            raise ContentType.DoesNotExist("Provided type_name is invalid.")

    def get_serializer_class(self, obj_class):
        serializer_class = None
        if obj_class is InsertOperation:
            serializer_class = InsertOperationSerializer
        elif obj_class is DeleteOperation:
            serializer_class = DeleteOperationSerializer
        elif obj_class is ReplaceOperation:
            serializer_class = ReplaceOperationSerializer
        return serializer_class

    def serialize_operations(self, operations):
        """Serialize a list of operations into JSON."""

        serialized_ops = []
        for operation in operations:
            serializer = self.get_serializer_class(operation.__class__)
            serialized_ops.append(serializer(operation).data)
        return serialized_ops

    def get(self, request, pzone_pk):
        """Get all the operations for a given pzone."""

        # attempt to get given pzone
        try:
            pzone = PZone.objects.get(pk=pzone_pk)
        except PZone.DoesNotExist:
            raise Http404("Cannot find given pzone.")

        # get operations and serialize them
        operations = PZoneOperation.objects.filter(pzone=pzone)

        # return a json response with serialized operations
        return Response(self.serialize_operations(operations), content_type="application/json")

    def post(self, request, pzone_pk):
        """Add a new operation to the given pzone, return json of the new operation."""

        # attempt to get given content list
        pzone = None
        try:
            pzone = PZone.objects.get(pk=pzone_pk)
        except PZone.DoesNotExist:
            raise Http404("Cannot find given pzone.")

        json_obj = []
        http_status = 500

        json_op = json.loads(request.body.decode("utf8"))
        if not isinstance(json_op, list):
            json_op = [json_op]

        for data in json_op:
            try:
                serializer = self.get_serializer_class_by_name(data["type_name"])
            except ContentType.DoesNotExist as e:
                json_obj = {"errors": [str(e)]}
                http_status = 400
                break

            serialized = serializer(data=data)
            if serialized.is_valid():
                # object is valid, save it
                serialized.save()

                # set response data
                json_obj.append(serialized.data)
                http_status = 200
            else:
                # object is not valid, return errors in a 400 response
                json_obj = serialized.errors
                http_status = 400
                break

        if http_status == 200 and len(json_obj) == 1:
            json_obj = json_obj[0]

        # cache the time in seconds until the next operation occurs
        next_ops = PZoneOperation.objects.filter(when__lte=timezone.now())
        if len(next_ops) > 0:
            # we have at least one operation, ordered soonest first
            next_op = next_ops[0]
            # cache with expiry number of seconds until op should exec
            cache.set('pzone-operation-expiry-' + pzone.name, next_op.when, 60 * 60 * 5)

        return Response(
            json_obj,
            status=http_status,
            content_type="application/json"
        )

    def delete(self, request, pzone_pk, operation_pk):
        """Remove an operation from the given pzone."""

        # note : we're not using the pzone_pk here since it's not actually
        #   necessary for getting an operation by pk, but it sure makes the urls
        #   nicer!

        # attempt to delete operation
        try:
            operation = PZoneOperation.objects.get(pk=operation_pk)
        except PZoneOperation.DoesNotExist:
            raise Http404("Cannot find given operation.")

        # delete operation
        operation.delete()

        # successful delete, return 204
        return Response("", 204)


class PZoneViewSet(UncachedResponse, viewsets.ModelViewSet):
    """Uncached viewset for `bulbs.promotions.PZone` model."""

    queryset = PZone.objects.all()
    serializer_class = PZoneSerializer
    paginate_by = 20
    permission_classes = [IsAdminUser, CanPromoteContent]

    def perform_update(self, serializer):
        """creates a record in the `bulbs.promotion.PZoneHistory`

        :param obj: the instance saved
        :param created: boolean expressing if the object was newly created (`False` if updated)
        """
        instance = serializer.save()
        # create history object
        instance.history.create(data=instance.data)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve pzone as a preview or applied if no preview is provided."""

        when_param = get_query_params(self.request).get("preview", None)
        pk = self.kwargs["pk"]

        when = None
        if when_param:
            try:
                when = parse_date(when_param)
            except ValueError:
                # invalid format, set back to None
                when = None

        pzone = None
        if when:
            # we have a date, use it
            pzone = PZone.objects.preview(pk=pk, when=when)
        else:
            # we have no date, just get the pzone
            pzone = PZone.objects.applied(pk=pk)

        # turn content list into json
        return Response(PZoneSerializer(pzone).data, content_type="application/json")
