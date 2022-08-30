from setuptools import setup

setup(
    name="puppet-tools",
    version="0.0.1",
    description="Puppet CLI tool for linting, validating",
    author="Bertus Wisman",
    install_requires=[
        'termcolor',
    ],
    entry_points={
        'console_scripts': [
            'puppet-tools=puppet_tools.main:entry'
        ]
    }
)
