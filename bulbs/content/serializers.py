from django.contrib import auth
from django.core.exceptions import ValidationError
from django.db import transaction
from django.template.defaultfilters import slugify

from rest_framework import serializers
from rest_framework import relations

from elastimorphic.serializers import ContentTypeField, PolymorphicSerializerMixin

from .models import Content, Tag, LogEntry


class ImageFieldSerializer(serializers.WritableField):

    def __init__(self, caption_field=None, alt_field=None, **kwargs):
        super(ImageFieldSerializer, self).__init__(**kwargs)

        self.caption_field = caption_field
        self.alt_field = alt_field

    def to_native(self, obj):
        data = {
            "id": obj.id,
        }
        if self.caption_field:
            data["alt"] = obj.alt
            data["caption"] = obj.caption
        return data

    def from_native(self, data):
        if data is None:
            return None

        image_id = data.get("id")
        if image_id is not None:
            return int(image_id)  # Just in case a string gets passed in

        return None

    def field_from_native(self, data, files, field_name, into):
        super(ImageFieldSerializer, self).field_from_native(data, files, field_name, into)
        image_data = data.get(field_name, {})
        if image_data is None:
            return

        if self.alt_field and "alt" in image_data:
            into[self.alt_field] = image_data["alt"]

        if self.caption_field and "caption" in image_data:
            into[self.caption_field] = image_data["caption"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag

    def to_native(self, obj):
        return {
            "id": obj.pk,
            "name": obj.name,
            "slug": obj.slug,
            "type": obj.get_mapping_type_name()
        }


class TagField(relations.RelatedField):
    """This is a relational field that handles the addition of tags to content
    objects. This field also allows the user to create tags in the db if they
    don't already exist."""

    read_only = False

    def to_native(self, obj):
        return {
            "id": obj.pk,
            "name": obj.name,
            "slug": obj.slug,
            "type": obj.get_mapping_type_name()
        }

    def from_native(self, value):
        """Basically, each tag dict must include a full dict with id,
        name and slug--or else you need to pass in a dict with just a name,
        which indicated that the Tag doesn't exist, and should be added."""

        if "id" in value:
            tag = Tag.objects.get(id=value["id"])
        else:
            if "name" not in value:
                raise ValidationError("Tags must include an ID or a name.")
            name = value["name"]
            slug = value.get("slug", slugify(name))
            try:
                tag = Tag.objects.get(slug=slug)
            except Tag.DoesNotExist:
                tag, created = Tag.objects.get_or_create(name=name, slug=slug)
        return tag


class UserSerializer(serializers.ModelSerializer):
    """"Returns basic User fields"""
    class Meta:
        model = auth.get_user_model()

    def to_native(self, obj):

        return {
            "id": obj.pk,
            "username": obj.username,
            "email": obj.email,
            "first_name": obj.first_name,
            "last_name": obj.last_name
        }


class AuthorField(relations.RelatedField):
    """This field manages the authors on a piece of content, and allows a "fatter"
    endpoint then would normally be possible with a RelatedField"""

    read_only = False

    def to_native(self, obj):
        return {
            "id": obj.pk,
            "first_name": obj.first_name,
            "last_name": obj.last_name,
            "username": obj.username
        }

    def from_native(self, value):
        """Basically, each author dict must include either a username or id."""
        model = auth.get_user_model()

        if "id" in value:
            author = model.objects.get(id=value["id"])
        else:
            if "username" not in value:
                raise ValidationError("Authors must include an ID or a username.")
            username = value["username"]
            author = model.objects.get(username=username)
        return author


class ContentSerializer(serializers.ModelSerializer):
    polymorphic_ctype = ContentTypeField(source="polymorphic_ctype_id", read_only=True)
    tags = TagField(many=True)
    authors = AuthorField(many=True)
    image = ImageFieldSerializer(required=False)
    absolute_url = serializers.Field(source="get_absolute_url")
    status = serializers.Field(source="get_status")

    class Meta:
        model = Content

    @transaction.commit_on_success
    def save(self, *args, **kwargs):
        if not "index" in kwargs:
            kwargs["index"] = False
        return super(ContentSerializer, self).save(*args, **kwargs)


class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry


class PolymorphicContentSerializer(PolymorphicSerializerMixin, ContentSerializer):
    pass
