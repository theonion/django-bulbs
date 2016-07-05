# from rest_framework import serializers
#
# from bulbs.content.serializers import ContentSerializer
# from bulbs.super_features.models import BaseSuperFeature


# class SuperFeatureDataField(serializers.Field):
#
#     def to_internal_value(self, data):
#         # TODO: Fix this
#         # serializer = get_data_serializer(self.parent.initial_data.get("superfeature_type"))
#         # return serializer().to_internal_value(data)
#         pass
#
#     def to_reprensentation(self, obj):
#         # TODO: Fix this
#         # serializer_class = get_data_serializer(self.parent.initial_data.get("superfeature_type"))
#         # serializer = serializer_class(data=obj)
#         # serializer.is_valid(raise_exception=True)
#         # return serializer.data
#         pass
#
#
# class SuperFeatureSerializer(ContentSerializer):
#
#     data = SuperFeatureDataField(required=False)
#
#     class Meta:
#         model = BaseSuperFeature
