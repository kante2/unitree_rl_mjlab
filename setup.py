"""Installation script for the 'unitree_rl_mjlab' python package."""

from setuptools import setup, find_packages

# Minimum dependencies required prior to installation
INSTALL_REQUIRES = [
    "mjlab==1.2.0",
    "mujoco-warp==3.5.0",
]

# Installation operation
setup(
    name="unitree_rl_mjlab",
    packages=find_packages(include=["src", "src.*"]),
    package_data={
        "src.assets.robots.unitree_go2": ["xmls/*.xml", "xmls/assets/*.obj"],
    },
    version="0.0.1",
    install_requires=INSTALL_REQUIRES,
)
