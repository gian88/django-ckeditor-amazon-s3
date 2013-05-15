import os, datetime
import re
import cStringIO
from urlparse import urlparse, urlunparse
from datetime import date

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from backends.s3boto import S3BotoStorage_AllPublic
from django.core.files.base import ContentFile

try:
    from PIL import Image, ImageOps
except ImportError:
    import Image
    import ImageOps

try:
    from django.views.decorators.csrf import csrf_exempt
except ImportError:
    # monkey patch this with a dummy decorator which just returns the
    # same function (for compatability with pre-1.1 Djangos)
    def csrf_exempt(fn):
        return fn

THUMBNAIL_SIZE = (75, 75)
S3BotoStorage = S3BotoStorage_AllPublic(bucket=settings.AWS_STORAGE_BUCKET_NAME)


def get_available_name(name):
    """
    Returns a filename that's free on the target storage system, and
    available for new content to be written to.
    """
    dir_name, file_name = os.path.split(name)
    file_root, file_ext = os.path.splitext(file_name)
    # If the filename already exists, keep adding an underscore (before the
    # file extension, if one exists) to the filename until the generated
    # filename doesn't exist.
    while os.path.exists(name):
        file_root += '_'
        # file_ext includes the dot.
        name = os.path.join(dir_name, file_root + file_ext)
    return name

def get_file_date():
    d = date.today()
    file_year = str(d.year)
    file_month = str(d.month).zfill(2)
    filenamepath = "%s/%s/" % (file_year, file_month)
    return filenamepath

def get_file_path(filename):
    ext = filename.split('.')[-1]
    filename_split = filename.rsplit('.', 1)
    file_name = filename_split[0]
    d = date.today()
    file_year = str(d.year)
    file_month = str(d.month).zfill(2)
    file_date = str(int(datetime.datetime.now().strftime("%s")) * 1000)
    filenamepath = "%s_%s.%s" % (file_name, file_date, ext)
    return filenamepath

def get_thumb_filename(file_name):
    """
    Generate thumb filename by adding _thumb to end of
    filename before . (if present)
    """
    return '%s_thumb%s' % os.path.splitext(file_name)


def create_thumbnail(out, filename, types):
    image = Image.open(cStringIO.StringIO(out))

    # Convert to RGB if necessary
    # Thanks to Limodou on DjangoSnippets.org
    # http://www.djangosnippets.org/snippets/20/
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')

    # scale and crop to thumbnail
    if types:
        imagefit = ImageOps.fit(image, THUMBNAIL_SIZE, Image.ANTIALIAS)
        imagefit = ImageOps.posterize(imagefit, 8)
        buf= cStringIO.StringIO()
        imagefit.save(buf, format= 'JPEG')
        S3BotoStorage.save(get_thumb_filename(filename), ContentFile(buf.getvalue()))
    else:
        imagefit = ImageOps.posterize(image, 8)
        buf= cStringIO.StringIO()
        imagefit.save(buf, format= 'JPEG')
        S3BotoStorage.save(filename, ContentFile(buf.getvalue()))



def get_media_url(path):
    """
    Determine system file's media URL.
    """
    url = S3BotoStorage.url(path)

    return url


def get_upload_filename(upload_name, user):
    # If CKEDITOR_RESTRICT_BY_USER is True upload file to user specific path.
    if getattr(settings, 'CKEDITOR_RESTRICT_BY_USER', False):
        user_path = user.username
    else:
        user_path = ''

    #function to create name of the file
    upload_name = get_file_path(upload_name)

    # Complete upload path (upload_path + date_path).
    upload_path = os.path.join(settings.CKEDITOR_UPLOAD_PATH, get_file_date())

    # Get available name and return.
    return os.path.join(upload_path,upload_name)


@csrf_exempt
def upload(request):
    """
    Uploads a file and send back its URL to CKEditor.

    TODO:
        Validate uploads
    """
    # Get the uploaded file from request.
    upload = request.FILES['upload']

    # Open output file in which to store upload.
    upload_filename = get_upload_filename(upload.name, request.user)
    out = r''

    # Iterate through chunks and write to destination.
    for chunk in upload.chunks():
        out += chunk
        create_thumbnail(out, upload_filename, False)

    create_thumbnail(out, upload_filename, True)

    # Respond with Javascript sending ckeditor upload url.
    url = S3BotoStorage.url(upload_filename)

    return HttpResponse("""
    <script type='text/javascript'>
        window.parent.CKEDITOR.tools.callFunction(%s, '%s');
    </script>""" % (request.GET['CKEditorFuncNum'], url))


def get_image_files(user=None):
    """
    Recursively walks all dirs under upload dir and generates a list of
    full paths for each file found.
    """
    # If a user is provided and CKEDITOR_RESTRICT_BY_USER is True,
    # limit images to user specific path, but not for superusers.
    if user and not user.is_superuser and getattr(settings, \
            'CKEDITOR_RESTRICT_BY_USER', False):
        user_path = user.username
    else:
        user_path = ''

    browse_path = S3BotoStorage.listdir(settings.CKEDITOR_UPLOAD_PATH)

    for filename in browse_path:
        # bypass for thumbs
        if not os.path.splitext(filename)[0].endswith('_thumb'):
            continue
        yield filename


def get_image_browse_urls(user=None):
    """
    Recursively walks all dirs under upload dir and generates a list of
    thumbnail and full image URL's for each file found.
    """
    images = []
    for filename in get_image_files(user=user):
        images.append({
            'thumb': get_media_url(filename),
            'src': quit_thumb(get_media_url(filename))
        })

    return images


def quit_thumb(filename):
    return filename.replace('_thumb', '')

def browse(request):
    context = RequestContext(request, {
        'images': get_image_browse_urls(request.user),
    })
    return render_to_response('browse.html', context)
