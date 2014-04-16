# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


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
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'content.content': {
            'Meta': {'object_name': 'Content'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '1024', 'blank': 'True'}),
            'feature_type': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('betty.cropped.fields.ImageField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
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