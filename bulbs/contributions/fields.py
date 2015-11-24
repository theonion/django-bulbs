from django.contrib.auth import get_user_model

from elasticsearch_dsl import field


class ContributorField(field.Object):

    def __init__(self, *args, **kwargs):
        super(ContributorField, self).__init__(*args, **kwargs)
        self.properties['username'] = field.String(index='not_analyzed')
        self.properties['is_freelance'] = field.Boolean()

    def to_es(self, obj):
        data = {
            'id': obj.id,
            'username': obj.username,
            'first_name': obj.first_name,
            'last_name': obj.last_name
        }
        profile = getattr(obj, 'freelanceprofile', None)
        if profile:
            data['is_freelance'] = profile.is_freelance
        return data

    def to_python(self, data):
        User = get_user_model()
        user = User.objects.filter(id=data['id'])
        if user.exists():
            return user.first()


class ContentContributionsField(field.Nested):
    """
    This needs a better long-term solution, but alas, time is cruel.
    """

    def __init__(self, *args, **kwargs):
        super(ContentContributionsField, self).__init__(*args, **kwargs)
        self.properties['contributor'] = ContributorField()

    def to_es(self, obj):
        data = {}
        return data

    def to_dict(self, **kwargs):
        return {}
