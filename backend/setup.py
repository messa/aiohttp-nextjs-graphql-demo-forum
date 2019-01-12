#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='forum-backend',
    version='0.0.1',
    packages=find_packages(exclude=['doc', 'tests*']),
    install_requires=[
        'aiohttp',
        'aiohttp-graphql',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'forum-backend=forum_backend:main',
        ],
    })
