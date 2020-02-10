# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 09:22:10 2020

"""

from os import path
import logging
import traceback

import cProfile
import pstats
from pstats import SortKey


filepath = path.dirname(path.abspath(__file__))
logfile = f'{path.basename(__file__).strip(".py")}.log'

logging.basicConfig(filename=path.join(filepath, '..', logfile), 
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# add logging to console
logging.getLogger().addHandler(logging.StreamHandler())


def main():
    try:
        from app import App, pygame_quit

        app_settings = {
            'window_width': 800,
            'window_height': 480,
            'FPS': 30
        }
        app = App(**app_settings)
        app.run()
    except Exception:
        logging.error(traceback.format_exc())
        # stop all parallel threads
        if hasattr(app, 'should_stop'):
            try:
                app.should_stop.set()
            except UnboundLocalError:
                pass
        # de-initialise pygame
        pygame_quit()


def print_profile():
    print('\n')
    # print only the most time consuming calls
    p = pstats.Stats(path.join(filepath, '..', 'data', 'profile'))
    p.sort_stats(SortKey.TIME).print_stats(50)


if __name__ == '__main__':
    cProfile.run('main()', 
                 path.join(filepath, '..', 'data', 'profile'))
    #print_profile()