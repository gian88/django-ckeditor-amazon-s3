Django Ckeditor Amazon S3
=========================

This project is based on  <https://github.com/shaunsephton/django-ckeditor> add the functionality the aws s3

The ckeditor comes preconfigured to use the Google Pretiffy for edit text code, this configuration the find the
file config.js inside the folder ckeditor

**Django admin CKEditor integration.**

Provides a ``RichTextField`` and ``CKEditorWidget`` utilizing CKEditor with image upload and browsing support included.

.. contents:: Contents
    :depth: 5

Installation
------------

Required
~~~~~~~~
#. Install or add django-ckeditor to your python path.

#. Add ``ckeditor`` to your ``INSTALLED_APPS`` setting.

#. Add a CKEDITOR_UPLOAD_PATH setting to the project's ``settings.py`` file. This setting specifies the folder to your CKEditor media upload directory in Amazon S3.

    CKEDITOR_UPLOAD_PATH = "uploads"

#. Add a AWS_DEFAULT_ACL setting to the project's ``settings.py`` file. This setting specifies the permissions(ACL) of the image access by the Amazon S3. The values
of the ACL is  ``private``, ``public-read``, ``public-read-write``, ``authenticated-read``.

    AWS_DEFAULT_ACL = 'public-read'

#. Run the ``collectstatic`` management command: ``$ /manage.py collectstatic``. This'll copy static CKEditor require media resources into the directory given by the ``STATIC_ROOT`` setting. See `Django's documentation on managing static files <https://docs.djangoproject.com/en/dev/howto/static-files>`_ for more info.

#. Add CKEditor URL include to your project's ``urls.py`` file::
    
    (r'^ckeditor/', include('ckeditor.urls')),    

#. Install boto the library amazon s3 <https://github.com/boto/boto>

Optional
~~~~~~~~
#. Set the CKEDITOR_RESTRICT_BY_USER setting to ``True`` in the project's ``settings.py`` file (default ``False``). This restricts access to uploaded images to the uploading user (e.g. each user only sees and uploads their own images). Superusers can still see all images. **NOTE**: This restriction is only enforced within the CKEditor media browser. 

#. Add a CKEDITOR_UPLOAD_PREFIX setting to the project's ``settings.py`` file. This setting specifies a URL prefix to media uploaded through CKEditor, i.e.::

       CKEDITOR_UPLOAD_PREFIX = "http://media.lawrence.com/media/ckuploads/
       
   (If CKEDITOR_UPLOAD_PREFIX is not provided, the media URL will fall back to MEDIA_URL with the difference of MEDIA_ROOT and the uploaded resource's full path and filename appended.)

#. Add a CKEDITOR_CONFIGS setting to the project's ``settings.py`` file. This specifies sets of CKEditor settings that are passed to CKEditor (see CKEditor's `Setting Configurations <http://docs.cksource.com/CKEditor_3.x/Developers_Guide/Setting_Configurations>`_), i.e.::

       CKEDITOR_CONFIGS = {
           'awesome_ckeditor': {
               'toolbar': 'Basic',
           },
       }
   
   The name of the settings can be referenced when instantiating a RichTextField::

       content = RichTextField(config_name='awesome_ckeditor')

   The name of the settings can be referenced when instantiating a CKEditorWidget::

       widget = CKEditorWidget(config_name='awesome_ckeditor')
   
   By specifying a set named ``default`` you'll be applying its settings to all RichTextField and CKEditorWidget objects for which ``config_name`` has not been explicitly defined ::
       
       CKEDITOR_CONFIGS = {
           'default': {
               'toolbar': 'Full',
               'height': 300,
               'width': 300,
           },
       }

Usage
-----

Field
~~~~~
The quickest way to add rich text editing capabilities to your models is to use the included ``RichTextField`` model field type. A CKEditor widget is rendered as the form field but in all other regards the field behaves as the standard Django ``TextField``. For example::

    from django.db import models
    from ckeditor.fields import RichTextField

    class Post(models.Model):
        content = RichTextField()


Widget
~~~~~~
Alernatively you can use the included ``CKEditorWidget`` as the widget for a formfield. For example::

    from django import forms
    from django.contrib import admin
    from ckeditor.widgets import CKEditorWidget

    from post.models import Post

    class PostAdminForm(forms.ModelForm):
        content = forms.CharField(widget=CKEditorWidget())
        class Meta:
            model = Post

    class PostAdmin(admin.ModelAdmin):
        form = PostAdminForm
    
    admin.site.register(Post, PostAdmin)

Amazon S3
~~~~~~~~~~
Add the following sentences in the setting to the project's ``settings.py`` file.

Add to ``TEMPLATE_CONTEXT_PROCESSORS`` in ``settings.py``::

    'django.core.context_processors.request'

If you want S3 storage as your default file back-end::

    # If you don't want this to be the global default, just make sure you
    # specify the S3BotoStorage_AllPublic backend on a per-field basis.
    DEFAULT_FILE_STORAGE = 'ckeditor.backends.s3boto.S3BotoStorage_AllPublic'

Then setup some values used by the backend::

    AWS_ACCESS_KEY_ID = 'YourS3AccessKeyHere'
    AWS_SECRET_ACCESS_KEY = 'YourS3SecretAccessKeyHere'
    AWS_STORAGE_BUCKET_NAME = 'OneOfYourBuckets'

If you would like to use a vanity domain instead of s3.amazonaws.com, you
first should configure it in amazon and then add this to settings::

    AWS_STORAGE_BUCKET_CNAME = 'static.yourdomain.com'

If you want a cache buster for your thumbnails (a string added to the end of
the image URL that causes browsers to re-fetch the image after changes), you
can set a value like this::

    MEDIA_CACHE_BUSTER = 'SomeValue'

You do not need to specify a cache buster.

If you aren't using the default S3 region, you can define it with the following
setting::

    AWS_REGION = 'us-east-1'

Managment Commands
~~~~~~~~~~~~~~~~~~
Included is a management command to create thumbnails for images already contained in ``CKEDITOR_UPLOAD_PATH``. This is useful to create thumbnails when starting to use django-ckeditor with existing images. Issue the command as follows::
    
    $ ./manage.py generateckeditorthumbnails

**NOTE**: If you're using custom views remember to include ckeditor.js in your form's media either through ``{{ form.media }}`` or through a ``<script>`` tag. Admin will do this for you automatically. See `Django's Form Media docs <http://docs.djangoproject.com/en/dev/topics/forms/media/>`_ for more info.

Change Log
----------

1.0
===

* Initial release.
