from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from picklefield import PickledObjectField

class PreferenceEntry(models.Model):
    label = models.CharField(max_length=256)
    value = PickledObjectField()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')


class PrefManager(object):

    def __init__(self, thing):
        self.thing = thing

    def get(self, label, default=None, autoset=None):
        return get_pref(self.thing, label, default, autoset)
    
    def set(self, label, value):
        set_pref(self.thing, label, value)


#FIXME: refatorar daqui pra baixo

def pref_exists(thing, label):

    c_type = ContentType.objects.get_for_model(thing)
    return PreferenceEntry.objects.filter(
                            content_type__pk=c_type.id,
                            object_id=thing.id,
                            label=label).exists()

def _get(thing, label):

    c_type = ContentType.objects.get_for_model(thing)

    return PreferenceEntry.objects.get(
                            content_type__pk=c_type.id,
                            object_id=thing.id,
                            label=label)

def set_pref(thing, label, value):

    if pref_exists(thing, label):
        preference = _get(thing, label)
    else:
        preference = PreferenceEntry()
        preference.content_object = thing
        preference.label = label

    preference.value = value
    preference.save()
    
    
def get_pref(thing, label, default=None, autoset=None):

    if pref_exists(thing, label):
        return _get(thing, label).value
    else:
        if autoset != None:
            set_pref(thing, label, autoset)
            return autoset
        else:
            if default != None:
                return default
            else:
                raise('There is no pref, autoset ou default value')