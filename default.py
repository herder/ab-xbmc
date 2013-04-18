#/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcgui
class MyClass(xbmcgui.Window):
    print "hello world!!!"

mydisplay = MyClass()
mydisplay.doModal()
del mydisplay