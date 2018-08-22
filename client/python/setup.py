from setuptools import setup, find_packages


setup(
    name='thegame',
    version='0.1a0',
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=[
        'grpcio',
        'PyQt5',
        'protobuf',
    ],
)
