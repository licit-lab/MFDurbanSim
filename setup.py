from setuptools import find_packages, setup

pkgs = find_packages(where="src")

setup_kwds = dict(
    name="mfdus",
    version="0.0.1",
    author="",
    author_email="",
    package_dir={"": "src"},
    packages=pkgs,
    description="Short description",
    long_description="Long description",
    url="",
    zip_safe=False
)

setup(**setup_kwds)