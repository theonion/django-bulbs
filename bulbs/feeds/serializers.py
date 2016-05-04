from rest_framework import serializers


class GlanceFeaturedMediaSerializer(serializers.Serializer):
    type = serializers.CharField()
    image = serializers.CharField()
    markup = serializers.CharField()

    def to_representation(self, obj):
        return {
            "type": "image",
            "image": obj.thumbnail.get_crop_url(ratio='1x1'),
            "markup": "",
        }


class GlanceContentSerializer(serializers.Serializer):

    type = serializers.IntegerField(required=True, allow_null=False)
    id = serializers.CharField()
    title = serializers.CharField()
    link = serializers.CharField()
    modified = serializers.DateTimeField()
    published = serializers.DateTimeField()
    slug = serializers.CharField()
    featured_media = GlanceFeaturedMediaSerializer
    authors = serializers.ListField(
        child=serializers.CharField()
    )
    tags = serializers.DictField(
        child=serializers.ListField(
            child=serializers.CharField()))

    def to_representation(self, obj):
        return {
            "type": "post",
            "id": obj.id,
            "title": obj.title,
            "modified": obj.last_modified.isoformat(),
            "published": obj.published.isoformat(),
            "slug": obj.slug,
            "featured_media": GlanceFeaturedMediaSerializer(obj).data,
            'link': self.context['request'].build_absolute_uri(obj.get_absolute_url()),
            'authors': ["America's Finest News Source"],  # TODO
            'tags': {
                'section': [tag.name for tag in obj.tags.all()],  # TODO: Ordered
            },
        }
