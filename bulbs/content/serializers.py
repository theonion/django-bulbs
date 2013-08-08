from django import forms
from rest_framework import serializers
from .models import Content, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag


class ContentSerializer(serializers.ModelSerializer):
    authors = serializers.ChoiceField(
        widget=forms.TextInput()
    )
    class Meta:
        model = Content

