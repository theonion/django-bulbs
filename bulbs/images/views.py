import os
import StringIO
import urllib2
from tempfile import mkstemp

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponseBadRequest, Http404
from django.conf import settings
from django.template import RequestContext

from PIL import Image as PImage

from afns.images.models import Image, ImageSubject, ImageAspectRatio, ImageSelection
from afns.images.tasks import clear_selection

def crop_ratios(request, image_id):
    try:
        image = Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        return not_found(request)
    ratios = ImageAspectRatio.objects.all()
    selections = [ImageSelection.objects.get_or_create_for_image_and_ratio(image, ratio) for ratio in ratios]
    
    if settings.DEBUG and getattr(settings, "IMAGE_CROP_FROM_HTTP", False) and not os.path.exists(image.location.path):
        if settings.SITE_NAME == 'onion':
            hack_media = "http://o.onionstatic.com/"
        elif settings.SITE_NAME == 'avclub':
            hack_media = "http://media.avclub.com/"
        image_url = "%s%s" % (hack_media, image.location)
    else:
        image_url = image.location.url

    context = {
        'image_url': image_url,
        'image': image,
        'ratios': ratios,
        'selections': selections,
    }
    if request.method == 'POST':
        ratio = get_object_or_404(ImageAspectRatio, slug=request.POST.get('ratio'))
        try:
            selection = ImageSelection.objects.get(aspectratio=ratio, image=image)
        except ImageSelection.DoesNotExist:
            selection = ImageSelection(aspectratio=ratio, image=image)

        selection.origin_x = int(request.POST.get('origin_x', '0'))
        selection.origin_y = int(request.POST.get('origin_y', '0'))
        selection.width = int(request.POST.get('width', '0'))
        selection.save()
        context['edited_ratio'] = ratio.slug
        clear_selection.delay(selection.id)

    response = render_to_response(
        "images/cropper.html", context, RequestContext(request),
    )
    return response
    
def crop_for_ratio(request, image_id, ratio_slug, width):
    width = int(width)
    if width > 1200:
        return HttpResponseBadRequest("Please send a message to an admin if you know what you're doing.")

    try:
        image = Image.objects.get(pk=image_id)
    except Image.DoesNotExist:
        return not_found(request)

    # theoretically this url should be proected by nginx if the file already exists
    # but as a fallback in case nginx isn't configured properly
    try:
        f = file(image.crop_path(ratio_slug, width, absolute=True), "rb+")
        response = HttpResponse(f.read())
        response['Content-Type'] = 'image/jpeg'
        response['Cache-Control'] = 'max-age=86400'
        return response
    except IOError:
        pass # generate file below

    try:
        im = PImage.open('%s/%s' % (settings.MEDIA_ROOT, image.location))
    except IOError:
        # if we can't open the file, we should 404, but if this is development we can fall back to
        # trying to retrieve the file via http for cropping
        if settings.DEBUG:
            if getattr(settings, "IMAGE_CROP_FROM_HTTP", False):
                if settings.SITE_NAME == 'onion':
                    hack_media = "http://o.onionstatic.com/"
                elif settings.SITE_NAME == 'avclub':
                    hack_media = "http://media.avclub.com/"
                else:
                    raise Http404
                f = StringIO.StringIO()
                try:
                    f.write(urllib2.urlopen("%s%s" % (hack_media, image.location)).read())
                except urllib2.HTTPError:
                    # if the file moved for some reason... return a placeholder
                    ratio = ImageAspectRatio.objects.get_for_slug(ratio_slug)
                    return HttpResponseRedirect("http://placehold.it/%sx%s" % ratio.get_size(width=width))

                f.seek(0)
                im = PImage.open(f)

                # if the image is loaded over http, it is not on the filesystem
                # and we will need to cache the image width and height for cropping with
                # imageselection below
                Image.objects.filter(pk=image.pk).update(_width=im.size[0], _height=im.size[1])
                image.width, image.height = im.size
            else:
                # if we're not enabled for cropping from HTTP, return a placeholder
                ratio = ImageAspectRatio.objects.get_for_slug(ratio_slug)
                return HttpResponseRedirect("http://placehold.it/%sx%s" % ratio.get_size(width=width))
        else:
            return HttpResponseNotFound("404: Not Found")

    if im.mode != "RGB":
        im = im.convert("RGB")

    # Add a comment tomorrow, Chris.
    if ratio_slug == 'original':
        height = (image.height * width) / image.width
    else:
        try:
            ratio = ImageAspectRatio.objects.get(slug=ratio_slug)
        except ImageAspectRatio.DoesNotExist:
            return not_found(request)
        selection = ImageSelection.objects.get_or_create_for_image_and_ratio(image, ratio)
        height = (ratio.height * int(width)) / ratio.width
        im = im.crop(selection.get_box())        
    
    im = im.resize((int(width), int(height)), PImage.ANTIALIAS)
    save_path = image.crop_path(ratio_slug, width, absolute=True)

    try:
        # Create the parent folder(s) for this crop.
        try:
            os.makedirs(os.path.split(save_path)[0])
        except (IOError, OSError): # this can happen if path exists
            pass
            
        f = file(save_path, "wb+")
        im.save(f, quality=90)
        f.seek(0)
        response = HttpResponse(f.read())
        f.close()
        response['Content-Type'] = 'image/jpeg'
        response['Cache-Control'] = 'max-age=86400'
        return response
    except (IOError, OSError): # this can happen if we don't have write access for this file
        import logging
        logger = logging.root
        logger.warning("Error generating image: %s" % (save_path))

        if settings.ADMIN_SITE or settings.DEBUG:
            out = StringIO.StringIO()
            im.save(out, "JPEG", quality=90)
            out.seek(0)
            response = HttpResponse(out.read())
            out.close()
            response['Content-Type'] = 'image/jpeg'
            response['Cache-Control'] = 'max-age=86400'
            return response
        else:
            return HttpResponseBadRequest("whoops")

def not_found(request):
    response = HttpResponseNotFound("404: Not Found")
    response['Cache-Control'] = 'max-age=600'
    return response
