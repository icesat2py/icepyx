# from gimli-org/gimli: https://github.com/gimli-org/gimli/blob/2e358dc6f5cb62afd696e20457c00e7c164d39af/doc/_templates/pybtex_plugins/setup.py on 29 Oct 2020

from setuptools import setup

setup(
    name="plugins",
    version="0.1.0",
    entry_points={
        "pybtex.style.formatting": ["mystyle = plugins:MyStyle"],
        "pybtex.style.labels": ["alpha = plugins:Alpha"],
    },
    py_modules=["pybtex_plugin"],
)
