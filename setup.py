#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

install_requires = [
    'pandas',
    'tqdm',
    'openpyxl',
    'xlsxwriter',
    'requests',
    'python-benedict',
    'PyYAML',
    'PyDrive',
]


setup(
    author='DataCebo',
    author_email='info@datacebo.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description='Scripts to extract multiple metrics from Github Projects.',
    entry_points={
        'console_scripts': [
            'github-analytics=github_analytics.__main__:main'
        ]
    },
    include_package_data=True,
    install_requires=install_requires,
    keywords='github-analytics',
    long_description=readme,
    long_description_content_type='text/markdown',
    name='github-analytics',
    packages=find_packages(include=['github_analytics', 'github_analytics.*']),
    python_requires='>=3.7,<3.10',
    version='0.0.1.dev0',
    zip_safe=False,
)
