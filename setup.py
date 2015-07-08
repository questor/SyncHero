from setuptools import setup
setup(
    name = "synchero",
    packages = ["synchero"],
    scripts = ["bin/synchero"],
    include_package_data = True,
    #package_data = {
    #    "synchero":
    #    [
    #        "appname/data/config/config.yaml",
    #    ]
    #},
    version = "0.5.0",
    description = "SyncHero tool",
    author = "questor",
    author_email = "questor@inter",
    url = "https://github.com/questor/synchero",
    #download_url = "https://github.com/myname/myapp/zipball/master",
    #keywords = ["my", "awesome", "app"],
    install_requires=[
    #    "package1 >= 1.4.1",
    #    "package2 == 0.8.9",
    ],
    license='LICENSE',
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development",
        ],
    long_description = open('README.md').read()
)
