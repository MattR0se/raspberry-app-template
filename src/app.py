# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 09:26:18 2020

"""

import pygame as pg
import pygame.freetype
import os
import logging
import threading
import inspect

import states

pygame_error = pg.error
pygame_quit = pg.quit


class App:
    def __init__(self, **settings):
        pg.init()
        self.settings = settings
        self.screen = pg.display.set_mode(
            (settings['window_width'],
             settings['window_height'])
        )
        self.screen_rect = self.screen.get_rect()
        self.clock = pg.time.Clock()
        self.fps = settings['FPS']
        self.running = True
        self.should_stop = threading.Event()
        self.window_flags = 0
        self.mouse_visible = True
        
        # load all assets
        self.base_dir = os.path.join(os.path.dirname(__file__), '..')
        self.assets_folder = os.path.join(self.base_dir, 'assets')
        self.data_folder = os.path.join(self.base_dir, 'data')
        
        # --- load Font files here ---
        # testfont_file = os.path.join(self.assets_folder, 'testfont.ttf')
        self.fonts = {
            # 'test': pygame.freetype.Font(testfont_file),
            'arial': pygame.freetype.SysFont('arial', size=32)
            }
        
        # load images
        sprite_files = list(
            filter(lambda x: x[-3:] == 'png', os.listdir(self.assets_folder)))
        self.sprite_images = {f[:-4]: pg.image.load(
            os.path.join(self.assets_folder, f)).convert_alpha()
                         for f in sprite_files}
        self.image = pg.Surface(self.screen_rect.size)
        self.image.fill(pg.Color(settings.get('background_color', 'red')))
        
        # setup the State Machine
        self.state_dict = {}
        self.state_name = 'Main'  # state at the start of the program
        self.state = None
        self.setup_states()
        
        # mirror the event queue
        self.event_queue = []
    

    def events(self):
        self.event_queue = []
        for event in pg.event.get():
            self.event_queue.append(event)
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if (event.key == pg.K_RETURN
                        and pg.key.get_pressed()[pg.K_LALT]):
                    # toggle fullscreen
                    self.window_flags = self.window_flags ^ pg.FULLSCREEN
                    self.mouse_visible = not self.mouse_visible
                    pg.mouse.set_visible(self.mouse_visible)
                    self.reset_app_screen()
                elif (event.key == pg.K_ESCAPE
                      and self.window_flags & pg.FULLSCREEN == pg.FULLSCREEN):
                    # exit fullscreen
                    self.window_flags = self.window_flags & ~pg.FULLSCREEN
                    self.mouse_visible = True
                    pg.mouse.set_visible(True)
                    self.reset_app_screen()
    
    
    def update(self, dt):
        if self.state.done:
            self.flip_state()
        self.state.update(dt)

        pg.display.set_caption(f'{round(self.clock.get_fps(), 1)}')
        
    
    def draw(self):
        self.state.draw(self.screen)
        
    
    def setup_states(self):
        # get a dictionary with all classes from the 'states' module
        self.state_dict = dict(inspect.getmembers(states, inspect.isclass))
        for key, state in self.state_dict.items():
            self.state_dict[key] = state(self)
        # remove the parent state class
        del self.state_dict['State']
        logging.debug(self.state_dict)
        # define the state at the start of the program
        self.state = self.state_dict[self.state_name]
        # set a states name for __repr__
        for name, state in self.state_dict.items():
            state.name = name
        self.state.startup()


    def flip_state(self):
        '''set the state to the next if the current state is done'''
        self.state.done = False
        # set the current and next state to the previous and current state
        previous, self.state_name = self.state_name, self.state.next
        self.state.cleanup()
        if self.state_name is None:
            self.running = False
        else:
            self.state = self.state_dict[self.state_name]
            self.state.startup()
            self.state.previous = previous


    def reset_app_screen(self):
        self.screen = pg.display.set_mode((
            self.settings['window_width'],
            self.settings['window_height']
        ), self.window_flags)
        self.screen_rect = self.screen.get_rect()
        self.state.redraw()
    
    
    def quit(self):
        # stop parallel threads
        self.should_stop.set()
        pg.quit()
    
    
    def run(self):
        while self.running:
            dt = self.clock.tick(self.fps) / 1000
            self.events()
            self.update(dt)
            self.draw()
        self.quit()