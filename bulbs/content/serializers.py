from django import forms
from rest_framework import serializers
from .models import Content, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag


class ContentSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='content-detail',
        lookup_field='pk'
    )
    tags = TagSerializer(many=True)

    class Meta:
        model = Content


class PolymorphicContentSerializer(ContentSerializer):
    def to_native(self, value):
        # TODO: allow per-class definitions of serializers like this:
        # real_serializer = value.get_serializer()
        # For now, here's the simplest possible thing:
        class ThisSerializer(serializers.ModelSerializer):
            class Meta:
                model = value.__class__
        real_serializer = ThisSerializer()
        return real_serializer.to_native(value)
