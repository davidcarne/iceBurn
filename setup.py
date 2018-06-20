# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='iCEburn',
    packages=find_packages(),
    install_requires=['pyusb'],
    python_requires='>3.5.2',
    version='0.1.0',
    description='Programmer for iCEblink40 boards',
    author='David Carne',
    author_email='davidcarne@gmail.com',
    url='https://github.com/tilk/iceBurn',
    keywords=['fpga', 'ice40', 'programmer'],
#    license='???',
    classifiers=[],
    entry_points={
        'console_scripts':[
            'iCEburn = iCEburn.__main__:main',
            'iCEreg = iCEburn.regtool:main'
        ]
    },
)

