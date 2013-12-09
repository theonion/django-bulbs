from django.contrib import auth
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError

from rest_framework import serializers
from rest_framework import relations

from .models import Content, Tag

from bulbs.images.fields import RemoteImageSerializer

import simplejson, time, hmac, hashlib, base64

class ContentTypeField(serializers.WritableField):
    """Converts between natural key for native use and integer for non-native."""
    def to_native(self, value):
        """Convert to natural key."""
        content_type = ContentType.objects.get_for_id(value)
        return '_'.join(content_type.natural_key())

    def from_native(self, value):
        """Convert to integer id."""
        natural_key = value.split('_')
        content_type = ContentType.objects.get_by_natural_key(*natural_key)
        return content_type.id


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag

    def to_native(self, obj):
        return {
            'id': obj.pk,
            'name': obj.name,
            'slug': obj.slug,
            'type': obj.get_mapping_type_name()
        }


class TagField(relations.RelatedField):
    """This is a relational field that handles the addition of tags to content
    objects. This field also allows the user to create tags in the db if they
    don't already exist."""

    read_only = False

    def to_native(self, obj):
        return {
            'id': obj.pk,
            'name': obj.name,
            'slug': obj.slug,
            'type': obj.get_mapping_type_name()
        }

    def from_native(self, value):
        """Basically, each tag dict must include a full dict with id,
        name and slug--or else you need to pass in a dict with just a name,
        which indicated that the Tag doesn't exist, and should be added."""

        if 'id' in value:
            tag = Tag.objects.get(id=value['id'])
        else:
            if 'name' not in value:
                raise ValidationError("Tags must include an ID or a name.")
            name = value['name']
            slug = value.get('slug', slugify(name))
            try:
                # Make sure that a tag with that slug doesn't already exist.
                tag = Tag.objects.get(slug=slug)
            except Tag.DoesNotExist:
                tag = Tag.objects.create(name=name, slug=slug)
        return tag


class UserSerializer(serializers.ModelSerializer):
    """"Returns basic User fields and an HMAC hash for Disqus authorization"""
    class Meta:
        model = auth.get_user_model()

    def to_native(self, obj):

        def get_remote_auth(user):
            data = simplejson.dumps({
                'id': user.pk,
                'username': user.username,
                'email': user.email,
            })
            message = base64.b64encode(data)
            timestamp = int(time.time())

            sig = hmac.HMAC(
                settings.DISQUS_SECRET, 
                '%s %s' % (message, timestamp), 
                hashlib.sha1
                ).hexdigest()

            return "%(message)s %(sig)s %(timestamp)s" % dict(
                message=message,
                timestamp=timestamp,
                sig=sig)

        return {
            'id': obj.pk,
            'username': obj.username,
            'email': obj.email,
            'first_name': obj.first_name,
            'last_name': obj.last_name,
            'remote_auth_s3': get_remote_auth(obj)
        }


class AuthorField(relations.RelatedField):
    """This field manages the authors on a piece of content, and allows a "fatter"
    endpoint then would normally be possible with a RelatedField"""

    read_only = False

    def to_native(self, obj):
        return {
            'id': obj.pk,
            'first_name': obj.first_name,
            'last_name': obj.last_name,
            'username': obj.username
        }

    def from_native(self, value):
        """Basically, each author dict must include either a username or id."""
        model = auth.get_user_model()

        if 'id' in value:
            author = model.objects.get(id=value['id'])
        else:
            if 'username' not in value:
                raise ValidationError("Authors must include an ID or a username.")
            username = value['username']
            author = model.objects.get(username=username)
        return author


class ContentSerializer(serializers.ModelSerializer):
    polymorphic_ctype = ContentTypeField(source='polymorphic_ctype_id', read_only=True)
    tags = TagField(many=True)
    authors = AuthorField(many=True)
    image = RemoteImageSerializer(required=False)

    class Meta:
        model = Content


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


