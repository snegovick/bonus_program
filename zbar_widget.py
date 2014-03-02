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

class ZBarWidget(gtk.Widget):
    def __init__(self):
        """Initialization"""
        
                #Initialize the Widget
        gtk.Widget.__init__(self)
        
