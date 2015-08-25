from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from djbetty.serializers import ImageFieldSerializer
from rest_framework.utils import model_meta
from rest_framework import relations
from rest_framework import serializers
from six import string_types

from .models import Content, Tag, LogEntry, FeatureType, TemplateType, ObfuscatedUrlInfo


class ContentTypeField(serializers.Field):
    """Converts between natural key for native use and integer for non-native."""
    def to_representation(self, value):
        """Convert to natural key."""
        content_type = ContentType.objects.get_for_id(value)
        return "_".join(content_type.natural_key())

    def to_internal_value(self, value):
        """Convert to integer id."""
        natural_key = value.split("_")
        content_type = ContentType.objects.get_by_natural_key(*natural_key)
        return content_type.id


class PolymorphicSerializerMixin(object):
    """Serialize a mix of polymorphic models with their own serializer classes."""
    def to_representation(self, value):
        if value:
            if hasattr(value, "get_serializer_class"):
                ThisSerializer = value.get_serializer_class()
            else:
                class ThisSerializer(serializers.ModelSerializer):
                    class Meta:
                        model = value.__class__

            serializer = ThisSerializer(context=self.context)
            return serializer.to_representation(value)
        else:
            return super(PolymorphicSerializerMixin, self).to_representation(value)


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50)  # this is actually limited by the slug

    class Meta:
        model = Tag

    def to_representation(self, obj):
        doc_type = obj.get_real_instance().mapping.doc_type
        return {
            "id": obj.pk,
            "name": obj.name,
            "slug": obj.slug,
            "type": doc_type
        }


class FeatureTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeatureType

    def to_representation(self, obj):
        return {
            "id": obj.pk,
            "name": obj.name,
            "slug": obj.slug,
        }


class TemplateTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = TemplateType

    def to_representation(self, obj):
        return {
            "id": obj.pk,
            "name": obj.name,
            "slug": obj.slug,
            "content_type": obj.content_type
        }


class TagField(relations.RelatedField):
    """This is a relational field that handles the addition of tags to content
    objects. This field also allows the user to create tags in the db if they
    don't already exist."""

    read_only = False

    def to_representation(self, obj):
        return {
            "id": obj.pk,
            "name": obj.name,
            "slug": obj.slug,
            "type": obj.__class__.search_objects.mapping.doc_type
        }

    def to_internal_value(self, value):
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

    def to_representation(self, obj):
        return obj.name

    def to_internal_value(self, value):
        """Basically, each tag dict must include a full dict with id,
        name and slug--or else you need to pass in a dict with just a name,
        which indicated that the FeatureType doesn't exist, and should be added."""
        if value == "":
            return None

        if isinstance(value, string_types):
            slug = slugify(value)
            feature_type, created = FeatureType.objects.get_or_create(
                slug=slug,
                defaults={"name": value}
            )
        else:
            if "id" in value:
                feature_type = FeatureType.objects.get(id=value["id"])
            elif "slug" in value:
                feature_type = FeatureType.objects.get(slug=value["slug"])
            else:
                raise ValidationError("Invalid feature type data")
        return feature_type


class DefaultUserSerializer(serializers.ModelSerializer):
    """Returns basic User fields"""

    class Meta:
        model = get_user_model()

    def to_representation(self, obj):

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

    def to_internal_value(self, data):
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
AUTHOR_FILTER = getattr(settings, "BULBS_AUTHOR_FILTER", {"is_staff": True})


class AuthorField(relations.RelatedField):
    """This field handles the addition/removal of authors to content"""

    read_only = False

    def to_representation(self, obj):
        return {
            "id": obj.pk,
            "username": obj.username,
            "email": obj.email,
            "first_name": obj.first_name,
            "last_name": obj.last_name,
            "full_name": obj.get_full_name(),
            "short_name": obj.get_short_name()
        }

    def to_internal_value(self, data):
        """Basically, each author dict must include either a username or id."""
        # model = get_user_model()
        model = get_user_model()

        if data is None:
            return None

        if "id" in data:
            author = model.objects.get(id=data["id"])
        elif "username" in data:
            author = model.objects.get(username=data["username"])
        else:
            raise ValidationError("Authors must include an ID or a username.")
        return author


class ContentSerializer(serializers.ModelSerializer):

    polymorphic_ctype = ContentTypeField(source="polymorphic_ctype_id", read_only=True)
    tags = TagField(allow_null=True, many=True, queryset=Tag.objects.all(), required=False)
    feature_type = FeatureTypeField(allow_null=True, queryset=FeatureType.objects.all(), required=False)
    authors = AuthorField(many=True, allow_null=True, queryset=get_user_model().objects.filter(**AUTHOR_FILTER), required=False)
    thumbnail = ImageFieldSerializer(allow_null=True, read_only=True)
    first_image = ImageFieldSerializer(allow_null=True, read_only=True)
    thumbnail_override = ImageFieldSerializer(allow_null=True, required=False)
    absolute_url = serializers.ReadOnlyField(source="get_absolute_url")
    status = serializers.ReadOnlyField(source="get_status")
    template_type = serializers.SlugRelatedField(
        slug_field="slug",
        allow_null=True,
        queryset=TemplateType.objects.all(),
        required=False)

    class Meta:
        model = Content

    def create(self, validated_data):
        ModelClass = self.Meta.model

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass.objects.create(**validated_data)
        except TypeError as exc:
            msg = (
                'Got a `TypeError` when calling `%s.objects.create()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.objects.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception text was: %s.' %
                (
                    ModelClass.__name__,
                    ModelClass.__name__,
                    self.__class__.__name__,
                    exc
                )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                setattr(instance, field_name, value)

        return instance


class LogEntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = LogEntry


class PolymorphicContentSerializer(PolymorphicSerializerMixin, ContentSerializer):
    pass


class ObfuscatedUrlInfoSerializer(serializers.ModelSerializer):

    content = serializers.PrimaryKeyRelatedField(queryset=Content.objects.all())
    expire_date = serializers.DateTimeField()
    create_date = serializers.DateTimeField()
    url_uuid = serializers.CharField(min_length=32, max_length=32, required=False)

    def validate(self, value):
        super(ObfuscatedUrlInfoSerializer, self).validate(value)
        if value["expire_date"] < value["create_date"]:
            raise serializers.ValidationError(
                "Start date must occur before expiration date.")
        return value

    class Meta:
        model = ObfuscatedUrlInfo
