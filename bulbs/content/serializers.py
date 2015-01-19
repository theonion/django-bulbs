from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.template.defaultfilters import slugify

from rest_framework import serializers
from rest_framework import relations

from elastimorphic.serializers import ContentTypeField, PolymorphicSerializerMixin

from .models import Content, Tag, LogEntry, FeatureType, ObfuscatedUrlInfo


class ImageFieldSerializer(serializers.WritableField):
    """
    serializer field type for images
    """

    def __init__(self, caption_field=None, alt_field=None, **kwargs):
        """instantiates object

        :param caption_field: caption
        :param alt_field: alt value
        :param kwargs: keyword arguments (optional)
        :return: `serializers.WriteableField`
        """
        super(ImageFieldSerializer, self).__init__(**kwargs)
        self.caption_field = caption_field
        self.alt_field = alt_field

    def to_native(self, obj):
        if obj is None or obj.id is None:
            return None
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
        # Just in case a string gets passed in
        if image_id is not None:
            return int(image_id)
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
    name = serializers.CharField(max_length=50)  # this is actually limited by the slug

    class Meta:
        model = Tag

    def to_native(self, obj):
        return {
            "id": obj.pk,
            "name": obj.name,
            "slug": obj.slug,
            "type": obj.get_mapping_type_name()
        }


class FeatureTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeatureType

    def to_native(self, obj):
        return {
            "id": obj.pk,
            "name": obj.name,
            "slug": obj.slug,
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
            if len(slugify(value["name"])) > 50:
                raise ValidationError("Maximum tag length is 50 characters.")

            name = value["name"]
            slug = value.get("slug", slugify(name))
            try:
                tag = Tag.objects.get(slug=slug)
            except Tag.DoesNotExist:
                tag, created = Tag.objects.get_or_create(name=name, slug=slug)
        return tag


class FeatureTypeField(relations.RelatedField):
    """This is a relational field that handles the addition of feature_types to
    content objects. This field also allows the user to create feature_types in
    the db if they don't already exist."""

    read_only = False

    def to_native(self, obj):
        return obj.name

    def from_native(self, value):
        """Basically, each tag dict must include a full dict with id,
        name and slug--or else you need to pass in a dict with just a name,
        which indicated that the Tag doesn't exist, and should be added."""
        if value == "":
            return None

        slug = slugify(value)
        feature_type, created = FeatureType.objects.get_or_create(
            slug=slug,
            defaults={"name": value}
        )
        return feature_type


class DefaultUserSerializer(serializers.ModelSerializer):
    """Returns basic User fields"""

    class Meta:
        model = get_user_model()
        # model = settings.AUTH_USER_MODEL

    def to_native(self, obj):

        json = {
            "id": obj.pk,
            "username": obj.username,
            "email": obj.email,
            "first_name": obj.first_name,
            "last_name": obj.last_name,
            "full_name": obj.get_full_name(),
            "short_name": obj.get_short_name()
        }

        return json

    def from_native(self, data, files):
        """Basically, each author dict must include either a username or id."""
        # model = get_user_model()
        model = self.Meta.model

        if "id" in data:
            author = model.objects.get(id=data["id"])
        else:
            if "username" not in data:
                raise ValidationError("Authors must include an ID or a username.")
            username = data["username"]
            author = model.objects.get(username=username)
        return author


UserSerializer = getattr(settings, "BULBS_USER_SERIALIZER", DefaultUserSerializer)


class ContentSerializer(serializers.ModelSerializer):

    polymorphic_ctype = ContentTypeField(source="polymorphic_ctype_id", read_only=True)
    tags = TagField(many=True)
    feature_type = FeatureTypeField(required=False)
    authors = UserSerializer(many=True, required=False, allow_add_remove=True, read_only=False)
    thumbnail = ImageFieldSerializer(required=False, read_only=True)
    first_image = ImageFieldSerializer(required=False, read_only=True)
    thumbnail_override = ImageFieldSerializer(required=False)
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


class ObfuscatedUrlInfoSerializer(serializers.ModelSerializer):

    expire_date = serializers.DateTimeField()
    create_date = serializers.DateTimeField()
    url_uuid = serializers.CharField(min_length=32, max_length=32)

    def validate(self, attrs):
        if attrs["expire_date"] < attrs["create_date"]:
            raise serializers.ValidationError(
                "Start date must occur before expiration date.")

    class Meta:
        model = ObfuscatedUrlInfo
