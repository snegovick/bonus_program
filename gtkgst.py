#!/usr/bin/env python

try:
        import gtk
        import gobject
        from gtk import gdk
except:
        raise SystemExit

import pygtk
if gtk.pygtk_version < (2, 0):
        print "PyGtk 2.0 or later required for this widget"
        raise SystemExit

import math
import Image
import numpy
import cairo
import camera_source
from os.path import exists, relpath
from sys import exit

# Gstreamer constants. 
# More infos about Gstreamer here : 
#  * http://www.cin.ufpe.br/~cinlug/wiki/index.php/Introducing_GStreamer
#  * http://www.oz9aec.net/index.php/gstreamer/345-a-weekend-with-gstreamer
gst_src             = 'v4l2src device=' # VideoForLinux driver asociated with specified device 
gst_src_format      = 'video/x-raw-yuv' # colorspace specific to webcam
gst_videosink       = 'appsink'     # sink habilitated to manage images
sep                 = ' ! '             # standard gstreamer pipe. Don't change that

class GtkGst(gtk.DrawingArea):
        __gsignals__ = { "expose-event": "override", "unrealize": "override" }
        def __init__(self, device, resolution):
                gtk.DrawingArea.__init__(self)
                self.connect("expose-event", self.do_expose_event)
                self.connect("unrealize", self.do_unrealize)
                self.resolution = resolution
                
                if not exists(device):
                        print device, 'not detected. Fall back to default camera (/dev/video0)'
                        self.device = '/dev/video0'
                else:
                        self.device = device             # device used for video input
                if not exists('/dev/video0'):
                        print "No webcam detected: /dev/video0 cannot be found.\n The program is now exiting."
                        exit()

                self.set_size_request(resolution[0], resolution[1])
                self.cs = camera_source.camerasrc(resolution[0], resolution[1], "/dev/video0")
                self.stopped = False
        
        def do_expose_event(self, widget, event):
                """This is where the widget must draw itself."""
                print "pull"
                
                if self.stopped == False:
                        self.img = self.cs.get_image()
                
                self.context = widget.window.cairo_create()
                
        # set a clip region for the expose event
                self.context.rectangle(event.area.x, event.area.y,
                                       event.area.width, event.area.height)
                self.context.clip()

                self.img.putalpha(256) # create alpha channel
                #imgd = img.tostring()
                #print "len(imgd):", len(imgd), "calc len:", 320*240*3
                arr = numpy.array(self.img)
                
                height, width, channels = arr.shape
                surface = cairo.ImageSurface.create_for_data(arr, cairo.FORMAT_RGB24, width, height)
                self.context.set_source_surface(surface, 0, 0)
                self.context.paint()
                gobject.timeout_add(100, self.queue_draw)
        #self.draw(self.context)
                
                return False

        #Draw the correct number of stars.  Each time you draw another star
        #move over by 22 pixels. which is the size of the star.
        def do_unrealize(self, arg):
                print "unrealize"
                self.cs.stop()

        def take_snapshot(self):
                """ Capture a snapshot from DrawingArea and save it into a image file """
                print "img:", self.img
                self.cs.stop()
                self.cs = camera_source.camerasrc(1280, 720, "/dev/video0")
                self.cs.stop()

                self.stopped = True
                return self.img

def snapshot_name():
        """ Return a string of the form yyyy-mm-dd-hms """
        from datetime import datetime
        today = datetime.today()
        y = str(today.year)
        m = str(today.month)
        d = str(today.day)
        h = str(today.hour)
        mi= str(today.minute)
        s = str(today.second)
        return '%s-%s-%s-%s%s%s' %(y, m, d, h, mi, s)
