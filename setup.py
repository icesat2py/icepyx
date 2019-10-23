import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="icepyx",
    version="0.0.1",
    author="Jessica Scheick",
    author_email="jbscheick@gmail.com",
    description="Processing ICESat-2 Elevations...",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ICESAT-2HackWeek/icesat2py.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
        
    ],
)