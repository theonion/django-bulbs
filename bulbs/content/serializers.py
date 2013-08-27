from django import forms
from django.contrib.auth.models import User
from rest_framework import serializers

from bulbs.images.models import Image

from .models import Content, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class SimpleAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image


class ContentSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='content-detail',
        lookup_field='pk'
    )
    tags = TagSerializer(many=True)
    authors = SimpleAuthorSerializer(many=True)
    image = ImageSerializer()

    class Meta:
        model = Content
        exclude = ('polymorphic_ctype',)


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
