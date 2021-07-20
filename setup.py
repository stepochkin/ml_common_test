#!/usr/bin/env python
# encoding=utf-8

from setuptools import setup, find_packages

test_deps = [
    "nose2",
    "mock",
]

setup(
    name="StepinTestLib",
    version="0.1",
    author="Stepochkin Alexander",
    author_email="stepochkin@mail.ru",
    description="Stepochkin Alexander test library",
    url='file://./dist',
    install_requires=[
        'numpy', 'scipy', 'scikit-learn'
    ],
    package_dir={'': 'lib'},
    packages=find_packages(
        'lib',
        exclude=['*.test']
    ),
    scripts=[],
    tests_require=["nose2", "mock"],
    test_suite='nose2.collector.collector',
    extras_require={
        'test': test_deps,
    },
    zip_safe=False,
)
