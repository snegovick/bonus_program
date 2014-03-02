#!/usr/bin/env python

try:
        import gtk
        import gobject
        from gtk import gdk
except:
        raise SystemExit

import math
import Image
import numpy
import cairo
from os.path import exists, relpath
from sys import exit


class GtkImg(gtk.DrawingArea):
        __gsignals__ = { "expose-event": "override", "unrealize": "override" }
        def __init__(self, image_file):
                gtk.DrawingArea.__init__(self)
                self.connect("expose-event", self.do_expose_event)
                self.img = Image.open(image_file)
                resolution = self.img.size
                
                self.set_size_request(resolution[0], resolution[1])
        
        def do_expose_event(self, widget, event):
                """This is where the widget must draw itself."""
                
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
                
                return False

