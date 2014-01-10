from django.db.models.signals import class_prepared

from .indexable import PolymorphicIndexable


# Registry for all PolymorphicIndexableModels in the project

class PolymorphicIndexableRegistry(object):
    def __init__(self):
        self.all_models = {}
        self.families = {}

    def register(self, klass):
        self.all_models[klass.get_mapping_type_name()] = klass
        base_class = klass.get_base_class()
        if not base_class in self.families:
            self.families[base_class] = {}
        self.families[base_class][klass.get_mapping_type_name()] = klass

    def get_doctypes(self, klass):
        base = klass.get_base_class()
        return self.families[base]


polymorphic_indexable_registry = PolymorphicIndexableRegistry()

def register_polymorphicindexables(sender, **kwargs):
    if not issubclass(sender, PolymorphicIndexable):
        return
    polymorphic_indexable_registry.register(sender)

class_prepared.connect(register_polymorphicindexables, dispatch_uid='polymorphicindexable_class_prepared')

