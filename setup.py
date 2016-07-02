from setuptools import setup

setup(
    name="keepass-menu",
    version="0.0.2",
    packages=["readkeepass", "readkeepass.kdb", "readkeepass.kdb.libkeepass"],
    author="Idaho Frost",
    author_email="frostidaho@gmail.com",
    description=("A library to read KeePass 1.x/KeePassX (v3) and KeePass "
                 "2.x (v4) files, and a user application to find keepass entries"
                 "using the dynamic menu rofi (which is similar to dmenu)"),
    license="GPL",
    keywords="keepass library, rofi, keepass, dmenu",
    url="https://github.com/frostidaho",  # project home page, if any
    scripts=['bin/keepass_rofi.py',],
    install_requires=[
        "lxml>=3.2.1",
        "pycrypto>=2.6.1",
        "tabulate>=0.7.5",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ]
)
