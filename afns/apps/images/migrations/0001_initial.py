# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ImageLicense'
        db.create_table('images_imagelicense', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
        ))
        db.send_create_signal('images', ['ImageLicense'])

        # Adding model 'ImageSubject'
        db.create_table('images_imagesubject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal('images', ['ImageSubject'])

        # Adding model 'ImageSource'
        db.create_table('images_imagesource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, db_index=True)),
        ))
        db.send_create_signal('images', ['ImageSource'])

        # Adding model 'Image'
        db.create_table('images_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['images.ImageSubject'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('license', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['images.ImageLicense'], null=True, blank=True)),
            ('altered', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('_width', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='width', blank=True)),
            ('_height', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='height', blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('location', self.gf('django.db.models.fields.files.ImageField')(max_length=255)),
            ('caption', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('alt', self.gf('django.db.models.fields.TextField')(max_length=255, blank=True)),
            ('credit', self.gf('django.db.models.fields.TextField')(max_length=255, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('images', ['Image'])

        # Adding unique constraint on 'Image', fields ['content_type', 'object_id']
        db.create_unique('images_image', ['content_type_id', 'object_id'])

        # Adding M2M table for field source on 'Image'
        db.create_table('images_image_source', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('image', models.ForeignKey(orm['images.image'], null=False)),
            ('imagesource', models.ForeignKey(orm['images.imagesource'], null=False))
        ))
        db.create_unique('images_image_source', ['image_id', 'imagesource_id'])

        # Adding model 'ImageAspectRatio'
        db.create_table('images_imageaspectratio', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('width', self.gf('django.db.models.fields.IntegerField')()),
            ('height', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('images', ['ImageAspectRatio'])

        # Adding model 'ImageSelection'
        db.create_table('images_imageselection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('aspectratio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['images.ImageAspectRatio'])),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['images.Image'])),
            ('origin_x', self.gf('django.db.models.fields.IntegerField')()),
            ('origin_y', self.gf('django.db.models.fields.IntegerField')()),
            ('width', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('images', ['ImageSelection'])

        # Adding unique constraint on 'ImageSelection', fields ['aspectratio', 'image']
        db.create_unique('images_imageselection', ['aspectratio_id', 'image_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ImageSelection', fields ['aspectratio', 'image']
        db.delete_unique('images_imageselection', ['aspectratio_id', 'image_id'])

        # Removing unique constraint on 'Image', fields ['content_type', 'object_id']
        db.delete_unique('images_image', ['content_type_id', 'object_id'])

        # Deleting model 'ImageLicense'
        db.delete_table('images_imagelicense')

        # Deleting model 'ImageSubject'
        db.delete_table('images_imagesubject')

        # Deleting model 'ImageSource'
        db.delete_table('images_imagesource')

        # Deleting model 'Image'
        db.delete_table('images_image')

        # Removing M2M table for field source on 'Image'
        db.delete_table('images_image_source')

        # Deleting model 'ImageAspectRatio'
        db.delete_table('images_imageaspectratio')

        # Deleting model 'ImageSelection'
        db.delete_table('images_imageselection')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'images.image': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'Image'},
            '_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'height'", 'blank': 'True'}),
            '_width': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'width'", 'blank': 'True'}),
            'alt': ('django.db.models.fields.TextField', [], {'max_length': '255', 'blank': 'True'}),
            'altered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'caption': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.TextField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['images.ImageLicense']", 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.files.ImageField', [], {'max_length': '255'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '255', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'source': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'images'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['images.ImageSource']"}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['images.ImageSubject']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'images.imageaspectratio': {
            'Meta': {'object_name': 'ImageAspectRatio'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        'images.imagelicense': {
            'Meta': {'object_name': 'ImageLicense'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'images.imageselection': {
            'Meta': {'unique_together': "(('aspectratio', 'image'),)", 'object_name': 'ImageSelection'},
            'aspectratio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['images.ImageAspectRatio']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['images.Image']"}),
            'origin_x': ('django.db.models.fields.IntegerField', [], {}),
            'origin_y': ('django.db.models.fields.IntegerField', [], {}),
            'width': ('django.db.models.fields.IntegerField', [], {})
        },
        'images.imagesource': {
            'Meta': {'object_name': 'ImageSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'})
        },
        'images.imagesubject': {
            'Meta': {'object_name': 'ImageSubject'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'})
        }
    }

    complete_apps = ['images']