#!/usr/bin/env python
# Copyright (C) 2012 by Kirik Konstantin <snegovick>

import pygst
import Image
pygst.require("0.10")
import gst
import sys


class camerasrc:
    def __init__(self, width, height, device):

        self.appsink = gst.parse_launch("appsink drop=true max-buffers=1")
        cf_yuv = gst.parse_launch("capsfilter caps=\"video/x-raw-yuv,width="+str(width)+",height="+str(height)+"\"")

        cf = gst.parse_launch("capsfilter caps=\"video/x-raw-rgb,width="+str(width)+",height="+str(height)+",bpp=24,red_mask=255, green_mask=65280, blue_mask=16711680, endianness=4321\"")
        ff = gst.element_factory_make("ffmpegcolorspace", "converter")
        src = gst.parse_launch("v4l2src device="+device)


        print "creating pipe"
        self.pipe = gst.Pipeline(name="ecvpipe")
        self.pipe.add(src)
        self.pipe.add(cf_yuv)
        self.pipe.add(ff)
        self.pipe.add(cf)
        self.pipe.add(self.appsink)
        print "done"
        src.link(cf_yuv)
        cf_yuv.link(ff)
        ff.link(cf)
        cf.link(self.appsink)
        print "setting state \"playing\""
        self.pipe.set_state(gst.STATE_PLAYING)
        self.imagewidth = width
        self.imageheight = height

    def get_image(self):
        data = self.appsink.emit("pull-buffer")
        if data == None:
            print "pull-buffer underrun (broken camera ?)"
            exit()
        pi = Image.fromstring("RGB", [self.imagewidth, self.imageheight], data)
        return pi

    def has_data(self):
        return True

    def stop(self):
        self.pipe.set_state(gst.STATE_NULL) 
