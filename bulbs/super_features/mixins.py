class SuperFeatureMixin(object):
    def get_absolute_url(self):
        if self.parent:
            return self.parent.get_absolute_url() + "/{}".format(self.slug)

        return "/{}".format(self.slug)

    @property
    def is_indexed(self):
        if self.parent:
            return False

        return self.indexed

    @property
    def is_parent(self):
        return self.parent is None

    @property
    def is_child(self):
        return self.parent is not None
