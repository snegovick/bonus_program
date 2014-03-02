# encoding: UTF-8
#!/usr/bin/env python

# example helloworld.py

import pygtk
pygtk.require('2.0')
import gtk
import zbarpygtk
import gtkgst
import uuid
import model, model_client
import gtkimg

class HelloWorld:

    def read_card_id(self):
        d = gtk.Dialog()
        d.add_buttons(gtk.STOCK_CANCEL, 2)
        self.code = None

        def set_status_label(opened, enabled):
            """update status button label to reflect indicated state."""
            if not opened:
                label = "closed"
            elif enabled:
                label = "enabled"
            else:
                label = "disabled"
            status_button.set_label(label)
                
        def status_button_toggled(button):
            """callback invoked when the status button changes state
            (interactively or programmatically).  ensures the zbar widget
            video streaming state is consistent and updates the display of the
            button to represent the current state
            """
            opened = zbar.get_video_opened()
            active = status_button.get_active()
            if opened and (active != zbar.get_video_enabled()):
                zbar.set_video_enabled(active)
            set_status_label(opened, active)
            if active:
                status_image.set_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
            else:
                status_image.set_from_stock(gtk.STOCK_NO, gtk.ICON_SIZE_BUTTON)

        def video_enabled(zbar, param):
            """callback invoked when the zbar widget enables or disables
            video streaming.  updates the status button state to reflect the
            current video state
            """
            enabled = zbar.get_video_enabled()
            if status_button.get_active() != enabled:
                status_button.set_active(enabled)

        def video_opened(zbar, param):
            """callback invoked when the zbar widget opens or closes a video
            device.  also called when a device is closed due to error.
            updates the status button state to reflect the current video state
            """
            opened = zbar.get_video_opened()
            status_button.set_sensitive(opened)
            set_status_label(opened, zbar.get_video_enabled())
            
        def decoded(zbar, data):
            print "decoded"
            self.code = data
            d.destroy()
            pass

        zbar = zbarpygtk.Gtk()
        zbar.connect("decoded-text", decoded)
        # enable/disable status button
        status_button = gtk.ToggleButton("closed")
        status_image = gtk.image_new_from_stock(gtk.STOCK_NO, gtk.ICON_SIZE_BUTTON)
        status_button.set_image(status_image)
        status_button.set_sensitive(False)

# bind status button state and video state
        status_button.connect("toggled", status_button_toggled)
        zbar.connect("notify::video-enabled", video_enabled)
        zbar.connect("notify::video-opened", video_opened)

        zbar.set_video_device("/dev/video0")
        zbar.set_size_request(1280, 720)
        zbar.show()
        d.vbox.pack_start(zbar)
        ret = d.run()
        d.destroy()
        print ret
        return self.code


    def read_card_cb(self, widget, data=None):
        code = self.read_card_id()

        rq_result = model.session.query(model.Client).filter_by(code=code).all()
        client = None
        if (len(rq_result) != 0):
            client = rq_result[0]

        if (client!=None):
            d = gtk.Dialog()
            d.add_buttons(gtk.STOCK_OK, 1)
            
            img = gtkimg.GtkImg("./pictures/"+client.picture+".jpg")
            d.vbox.pack_start(img)
            code_label = gtk.Label("Код:"+client.code)
            d.vbox.pack_start(code_label)
            d.show_all()
            d.run()
            d.destroy()
        else:

            d = gtk.MessageDialog(self.window, 
                                  gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, 
                                  gtk.BUTTONS_CLOSE, "Клиент с таким кодом не найден")
            d.run()
            d.destroy()
        
        print client

    def new_client_cb(self, widget, data=None):
        d = gtk.Dialog()
        #d.add_buttons(gtk.STOCK_OK, 1, gtk.STOCK_CANCEL, 2)
        camera = gtkgst.GtkGst("/dev/video0", [320, 240])
        d.vbox.pack_start(camera)
        capture = gtk.Button("Сфотографировать")
        get_code = gtk.Button("Получить код")
        save = gtk.Button("Сохранить")
        cancel = gtk.Button("Отмена")
        code_label = gtk.Label("Код:")
        self.code = None
        self.image = None

        def capture_cb(*kwargs):
            self.image = camera.take_snapshot()
            get_code.set_sensitive(True)
            capture.set_sensitive(False)
            print "capture"

        def get_code_cb(*kwargs):
            self.code = self.read_card_id()
            if (self.code != None):
                code_label.set_text("Код: "+str(self.code))
                save.set_sensitive(True)
            else:
                code_label.set_text("Код не распознан")

        def save_cb(*kwargs):
            if (self.image != None) and (self.code != None):
                img_code = self.code.encode('base64').rstrip('=\n').replace('/', '_')
                img_path = "./pictures/"+img_code+".jpg"
                self.image.save(img_path)
                c = model_client.Client(self.code, img_code)
                model.session.add(c)
                model.session.commit()
                d.destroy()

        def cancel_cb(*kwargs):
            d.destroy()            

        capture.connect("clicked", capture_cb, None)
        get_code.connect("clicked", get_code_cb, None)
        save.connect("clicked", save_cb, None)
        cancel.connect("clicked", cancel_cb, None)
            
        d.vbox.pack_start(capture)
        d.vbox.pack_start(code_label)
        d.vbox.pack_start(get_code)

        hbox = gtk.HBox()
        hbox.pack_start(save)
        hbox.pack_start(cancel)
        d.vbox.pack_start(hbox)
        get_code.set_sensitive(False)
        save.set_sensitive(False)

        d.show_all()
        ret = d.run()
        d.destroy()
        print self.image
        print ret

    def settings_cb(self, widget, data=None):
        print "settings called"

    def delete_event(self, widget, event, data=None):
        print "delete event occurred"
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.gdk.threads_leave()
        gtk.main_quit()

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.menu_box = gtk.VBox(False, 0)
    
        self.window.connect("delete_event", self.delete_event)    
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)

        self.read_card = gtk.Button(u"Прочитать карточку")
        self.read_card.connect("clicked", self.read_card_cb, None)
        self.menu_box.pack_start(self.read_card)

        self.new_client = gtk.Button(u"Завести клиента")
        self.new_client.connect("clicked", self.new_client_cb, None)
        self.menu_box.pack_start(self.new_client)

        mb = gtk.MenuBar()

        filemenu = gtk.Menu()
        filem = gtk.MenuItem("File")
        filem.set_submenu(filemenu)
       
        settings = gtk.MenuItem("Настройки")
        settings.connect("activate", self.settings_cb)
        filemenu.append(settings)

        exit = gtk.MenuItem("Выход")
        exit.connect("activate", gtk.main_quit)
        filemenu.append(exit)

        mb.append(filem)
        self.menu_box.pack_start(mb, False, False, 0)

        self.window.add(self.menu_box)
        self.window.show_all()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    gtk.gdk.threads_init()
    gtk.gdk.threads_enter()

    hello = HelloWorld()
    hello.main()

    gtk.gdk.threads_leave()
