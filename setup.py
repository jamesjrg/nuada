from setuptools import setup

setup(
    name="nuada",
    entry_points={"console_scripts": ["nuada = nuada.main:hello"]},
)
