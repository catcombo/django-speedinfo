# coding: utf-8

from os.path import join, dirname
from setuptools import setup


with open(join(dirname(__file__), 'README.rst')) as f:
    long_description = f.read()

setup(
    name='django-speedinfo',
    version='1.2',
    packages=['speedinfo', 'speedinfo.migrations'],
    include_package_data=True,
    install_requires=['Django'],
    license='MIT',
    description='Live profiling tool for Django framework to measure views performance',
    long_description=long_description,
    url='https://github.com/catcombo/django-speedinfo',
    author='Evgeniy Krysanov',
    author_email='evgeniy.krysanov@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords='django profiler views performance',
)
