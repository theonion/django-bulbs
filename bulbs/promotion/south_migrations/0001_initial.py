# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


# Safe User import for Django < 1.5
try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
else:
    User = get_user_model()
# from django.conf import settings
# from django.db.models.loading import get_model
# User = get_model(*settings.AUTH_USER_MODEL.split("."))


# With the default User model these will be 'auth.User' and 'auth.user'
# so instead of using orm['auth.User'] we can use orm[user_orm_label]
user_orm_label = '%s.%s' % (User._meta.app_label, User._meta.object_name)
user_model_label = '%s.%s' % (User._meta.app_label, User._meta.module_name)


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ContentListOperation'
        db.create_table(u'promotion_contentlistoperation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'polymorphic_promotion.contentlistoperation_set', null=True, to=orm['contenttypes.ContentType'])),
            ('content_list', self.gf('django.db.models.fields.related.ForeignKey')(related_name='operations', to=orm['promotion.ContentList'])),
            ('when', self.gf('django.db.models.fields.DateTimeField')()),
            ('applied', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'promotion', ['ContentListOperation'])

        # Adding model 'InsertOperation'
        db.create_table(u'promotion_insertoperation', (
            (u'contentlistoperation_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['promotion.ContentListOperation'], unique=True, primary_key=True)),
            ('index', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['content.Content'])),
            ('lock', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'promotion', ['InsertOperation'])

        # Adding model 'ReplaceOperation'
        db.create_table(u'promotion_replaceoperation', (
            (u'contentlistoperation_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['promotion.ContentListOperation'], unique=True, primary_key=True)),
            ('content', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['content.Content'])),
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['content.Content'])),
            ('lock', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'promotion', ['ReplaceOperation'])

        # Adding model 'LockOperation'
        db.create_table(u'promotion_lockoperation', (
            (u'contentlistoperation_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['promotion.ContentListOperation'], unique=True, primary_key=True)),
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['content.Content'])),
        ))
        db.send_create_signal(u'promotion', ['LockOperation'])

        # Adding model 'UnlockOperation'
        db.create_table(u'promotion_unlockoperation', (
            (u'contentlistoperation_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['promotion.ContentListOperation'], unique=True, primary_key=True)),
            ('target', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', to=orm['content.Content'])),
        ))
        db.send_create_signal(u'promotion', ['UnlockOperation'])

        # Adding model 'ContentList'
        db.create_table(u'promotion_contentlist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('length', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('data', self.gf('json_field.fields.JSONField')(default=[])),
        ))
        db.send_create_signal(u'promotion', ['ContentList'])

        # Adding model 'ContentListHistory'
        db.create_table(u'promotion_contentlisthistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_list', self.gf('django.db.models.fields.related.ForeignKey')(related_name='history', to=orm['promotion.ContentList'])),
            ('data', self.gf('json_field.fields.JSONField')(default=[])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'promotion', ['ContentListHistory'])


    def backwards(self, orm):
        # Deleting model 'ContentListOperation'
        db.delete_table(u'promotion_contentlistoperation')

        # Deleting model 'InsertOperation'
        db.delete_table(u'promotion_insertoperation')

        # Deleting model 'ReplaceOperation'
        db.delete_table(u'promotion_replaceoperation')

        # Deleting model 'LockOperation'
        db.delete_table(u'promotion_lockoperation')

        # Deleting model 'UnlockOperation'
        db.delete_table(u'promotion_unlockoperation')

        # Deleting model 'ContentList'
        db.delete_table(u'promotion_contentlist')

        # Deleting model 'ContentListHistory'
        db.delete_table(u'promotion_contentlisthistory')


    models = {
        user_model_label: {
            'Meta': {'object_name': User.__name__, 'db_table': "'%s'" % User._meta.db_table},
            User._meta.pk.attname: ('django.db.models.fields.AutoField', [], {'primary_key': 'True', 'db_column': "'%s'" % User._meta.pk.column}),
        },
        u'content.content': {
            'Meta': {'object_name': 'Content'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['%s']" % user_orm_label, 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '1024', 'blank': 'True'}),
            'feature_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('djbetty.fields.ImageField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'indexed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_content.content_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'subhead': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['content.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'content.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_content.tag_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'promotion.contentlist': {
            'Meta': {'object_name': 'ContentList'},
            'data': ('json_field.fields.JSONField', [], {'default': '[]'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'promotion.contentlisthistory': {
            'Meta': {'object_name': 'ContentListHistory'},
            'content_list': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'history'", 'to': u"orm['promotion.ContentList']"}),
            'data': ('json_field.fields.JSONField', [], {'default': '[]'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'promotion.contentlistoperation': {
            'Meta': {'ordering': "['-when']", 'object_name': 'ContentListOperation'},
            'applied': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_list': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'operations'", 'to': u"orm['promotion.ContentList']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'polymorphic_ctype': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'polymorphic_promotion.contentlistoperation_set'", 'null': 'True', 'to': u"orm['contenttypes.ContentType']"}),
            'when': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'promotion.insertoperation': {
            'Meta': {'ordering': "['-when']", 'object_name': 'InsertOperation', '_ormbases': [u'promotion.ContentListOperation']},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['content.Content']"}),
            u'contentlistoperation_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['promotion.ContentListOperation']", 'unique': 'True', 'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'lock': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'promotion.lockoperation': {
            'Meta': {'ordering': "['-when']", 'object_name': 'LockOperation', '_ormbases': [u'promotion.ContentListOperation']},
            u'contentlistoperation_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['promotion.ContentListOperation']", 'unique': 'True', 'primary_key': 'True'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['content.Content']"})
        },
        u'promotion.replaceoperation': {
            'Meta': {'ordering': "['-when']", 'object_name': 'ReplaceOperation', '_ormbases': [u'promotion.ContentListOperation']},
            'content': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['content.Content']"}),
            u'contentlistoperation_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['promotion.ContentListOperation']", 'unique': 'True', 'primary_key': 'True'}),
            'lock': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['content.Content']"})
        },
        u'promotion.unlockoperation': {
            'Meta': {'ordering': "['-when']", 'object_name': 'UnlockOperation', '_ormbases': [u'promotion.ContentListOperation']},
            u'contentlistoperation_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['promotion.ContentListOperation']", 'unique': 'True', 'primary_key': 'True'}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'to': u"orm['content.Content']"})
        }
    }

    complete_apps = ['promotion']
