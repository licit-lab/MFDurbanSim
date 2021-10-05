from setuptools import find_packages, setup

pkgs = find_packages(where="src")

setup_kwds = dict(
    name="mfdurbansim",
    version="0.0.1",
    author="",
    author_email="",
    package_dir={"": "src"},
    packages=pkgs,
    entry_points={
        'console_scripts': ['MFDUrbanSimLauncher=mfdurbansim.Main:main',
                            'MFDUrbanSimRender=mfdurbansim.Script_Visualisation:main'],
    },
    description="Short description",
    long_description="Long description",
    url="",
    zip_safe=False
)

setup(**setup_kwds)