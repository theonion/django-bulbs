from rest_framework import serializers

from .models import LiveBlogEntry


class LiveBlogEntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = LiveBlogEntry
