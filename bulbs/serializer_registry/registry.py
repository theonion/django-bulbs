

class DataSerializerRegistry(object):

    def __init__(self):
        self.registry = dict()

    def register(self, key, name, serializer):
        if key in self.registry:
            raise KeyError(
                '''
                There is already a serializer registered with the provided key, {0}
                '''.format(key)
            )
        self.registry[key] = (name, serializer)

    def choices(self):
        return tuple(
            (key, values[0]) for key, values in self.registry.items()
        )

    def serializers(self):
        return dict(
            (key, values[1]) for key, values in self.registry.items()
        )
