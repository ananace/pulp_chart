#!/usr/bin/env python3

from setuptools import find_packages, setup

requirements = ["pulpcore>=3.0.0rc7"]

setup(
    name="pulp-chart",
    version="0.1.0a1",
    description="pulp_chart plugin for the Pulp Project",
    license="GPLv2+",
    author="Alexander Olofsson",
    author_email="alexander.olofsson@liu.se",
    url="https://github.com/ananace/pulp_chart",
    python_requires=">=3.6",
    install_requires=requirements,
    include_package_data=True,
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=(
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: POSIX :: Linux",
        "Framework :: Django",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ),
    entry_points={"pulpcore.plugin": ["pulp_chart = pulp_chart:default_app_config"]},
)
