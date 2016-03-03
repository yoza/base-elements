#!/usr/bin/env python3

from setuptools import find_packages, setup


setup(name='elements',
      version='1.2',
      description='Django base templatetags',
      author='Oleg Prans',
      author_email='oleg@prans.net',
      url='https://github.com/yoza/base-elements.git',
      packages=find_packages(),
      include_package_data=True,
      package_data={'elements': ['templates/admin/*.html',
                                 'templates/admin/edit_inline/*.html',
                                 'templates/admin/elements/*.html',
                                 'templates/blocks/*.html',
                                 'templates/elements/*.html',
                                 'static/elements/*/*.*',
                                 'static/elements/*/src/*.css',
                                 'locale/*/*/*.*']},
      install_requires=['six',
                        'markdown2',
                        'Pillow'],
      zip_safe=False)
