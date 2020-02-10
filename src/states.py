# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 09:40:41 2020

"""

import pygame as pg
import logging


class State(object):
    def __init__(self, app):
        self.app = app
        self.next = None  # what comes after if this is done
        self.done = False  # if true, the next state gets executed
        self.previous = None  # the state that was executed before

        if not hasattr(self, 'name'):
            self.name = 'State'

    def __repr__(self):
        return self.name

    def startup(self):
        pass

    def cleanup(self):
        pass

    def get_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass
    
    def redraw(self):
        pass


class Main(State):
    """
    This is the default state
    """
    def __init__(self, app):
        State.__init__(self, app)
        self.next = None