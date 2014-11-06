# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CmsNotification'
        db.create_table(u'cms_notifications_cmsnotification', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=110)),
            ('body', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('post_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('notify_end_date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'cms_notifications', ['CmsNotification'])


    def backwards(self, orm):
        # Deleting model 'CmsNotification'
        db.delete_table(u'cms_notifications_cmsnotification')


    models = {
        u'cms_notifications.cmsnotification': {
            'Meta': {'ordering': "['-id']", 'object_name': 'CmsNotification'},
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notify_end_date': ('django.db.models.fields.DateTimeField', [], {}),
            'post_date': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '110'})
        }
    }

    complete_apps = ['cms_notifications']