from setuptools import setup

setup(
    name='gw2chars',
    version='1.0.0',
    description='GW2 Character Gear Overview',
    packages=['gw2chars'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)