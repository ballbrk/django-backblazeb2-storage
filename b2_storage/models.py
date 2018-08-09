# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class FileUpload(models.Model):
    file_id = models.CharField(max_length=255, db_index=True, primary_key=True)
    name = models.CharField(max_length=400, verbose_name=_(u'file name'),db_index=True)
    content_sha1 = models.CharField(max_length=150,db_index=True)

    def __str__(self):
        return self.file_id

    class Meta:
        verbose_name = _('B2 file Upload')
        verbose_name_plural = _('B2 file Uploads')
        unique_together = ("file_id", "name")