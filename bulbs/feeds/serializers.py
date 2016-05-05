from rest_framework import serializers


class GlanceContentSerializer(serializers.Serializer):

    type = serializers.IntegerField(required=True, allow_null=False)
    id = serializers.CharField()
    title = serializers.CharField()
    link = serializers.URLField()
    modified = serializers.DateTimeField()
    published = serializers.DateTimeField()
    slug = serializers.CharField()
    images = serializers.DictField(
        child=serializers.URLField()
    )
    authors = serializers.ListField(
        child=serializers.CharField()
    )
    tags = serializers.DictField(
        child=serializers.ListField(
            child=serializers.CharField()))

    def to_representation(self, obj):
        return {
            'type': 'post',
            'id': obj.id,
            'title': obj.title,
            'modified': obj.last_modified.isoformat(),
            'published': obj.published.isoformat(),
            'slug': obj.slug,
            'images': {
                'post-16-9-thumbnail': obj.thumbnail.get_crop_url(ratio='16x9'),
            },
            'link': self.context['request'].build_absolute_uri(obj.get_absolute_url()),
            # mparent(2016-05-04) TODO: Optional author support
            'authors': ["America's Finest News Source"],
            'tags': {
                'section': [tag.name for tag in obj.ordered_tags()],
            },
        }
