import setuptools

with open("README.rst", "r") as f:
    LONG_DESCRIPTION = f.read()

with open("requirements.txt") as f:
    INSTALL_REQUIRES = f.read().strip().split("\n")

EXTRAS_REQUIRE = {
    "viz": ["geoviews >= 1.9.0", "cartopy >= 0.18.0", "scipy"],
    "cloud": ["s3fs"],
}
EXTRAS_REQUIRE["complete"] = sorted(set(sum(EXTRAS_REQUIRE.values(), [])))

setuptools.setup(
    name="icepyx",
    author="The icepyx Developers",
    author_email="jbscheick@gmail.com",
    maintainer="Jessica Scheick",
    maintainer_email="jbscheick@gmail.com",
    description="Python tools for obtaining and working with ICESat-2 data",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    url="https://github.com/icesat2py/icepyx.git",
    license="BSD 3-Clause",
    packages=setuptools.find_packages(exclude=["*tests"]),
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires=">=3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
    ],
    py_modules=["_icepyx_version"],
    use_scm_version={
        "fallback_version": "unknown",
        "local_scheme": "node-and-date",
        "write_to": "_icepyx_version.py",
        "write_to_template": 'version = "{version}"\n',
    },
    setup_requires=["setuptools>=30.3.0", "wheel", "setuptools_scm"],
)
