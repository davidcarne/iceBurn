# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='iCEburn',
    packages=find_packages(),
    install_requires=['pyusb'],
    python_requires='>3.3',
    version='0.1.1',
    description='Programmer for iCEblink40 boards',

    long_description=long_description,
    long_description_content_type="text/markdown",

    author='David Carne',
    author_email='davidcarne@gmail.com',
    url='https://github.com/davidcarne/iceBurn',
    keywords=['fpga', 'ice40', 'programmer'],
    license='BSD',
    classifiers=(
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.0",
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts':[
            'iCEburn = iCEburn.__main__:main',
            'iCEreg = iCEburn.regtool:main'
        ]
    },
)

