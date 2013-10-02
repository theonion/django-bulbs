from django import forms
from django.contrib import auth
from django.template.defaultfilters import slugify

from rest_framework import serializers

from .models import Content, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = auth.get_user_model()
        exclude = ('password',)


class SimpleAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = auth.get_user_model()
        fields = ('id', 'first_name', 'last_name', 'username')


class ContentSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, required=False)
    authors = serializers.PrimaryKeyRelatedField(many=True, required=False)

    class Meta:
        model = Content

    def to_native(self, *args, **kwargs):
        data = super(ContentSerializer, self).to_native(*args, **kwargs)
        data['feature_type.slug'] = slugify(data['feature_type'])
        return data


class ContentSerializerReadOnly(ContentSerializer):
    tags = TagSerializer(many=True, required=False)
    authors = SimpleAuthorSerializer(many=True, required=False)


class PolymorphicContentSerializerMixin(object):
    def to_native(self, value):
        if value:
            if hasattr(value, 'get_serializer_class'):
                ThisSerializer = value.get_serializer_class()
            else:
                class ThisSerializer(serializers.ModelSerializer):
                    class Meta:
                        model = value.__class__
            
            serializer = ThisSerializer(context=self.context)
            return serializer.to_native(value)
        else:
            return super(PolymorphicContentSerializerMixin, self).to_native(value)


class PolymorphicContentSerializer(PolymorphicContentSerializerMixin, ContentSerializer):
    pass


class PolymorphicContentSerializerReadOnly(PolymorphicContentSerializerMixin, ContentSerializerReadOnly):
    pass

