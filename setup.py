# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 19:47:01 2023

@author: apraa
"""

from distutils.core import setup
import py2exe

setup(
    console=['Video_player_v2.py'],
    py_modules=['my_functions'],
    options={
            'py2exe': {
                'bundle_files': 1,
                'compressed': True,
                'excludes': ['pkg_resources']
            }
        },
    zipfile=None
)