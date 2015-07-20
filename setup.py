from __future__ import with_statement
from setuptools import setup
import os
from os.path import join as pjoin, splitext, split as psplit
from distutils.core import setup
from distutils.command.install_scripts import install_scripts
from distutils import log

# from here: https://matthew-brett.github.io/pydagogue/installing_scripts.html

BAT_TEMPLATE = \
r"""@echo off
set mypath=%~dp0
set pyscript="%mypath%{FNAME}"
set /p line1=<%pyscript%
if "%line1:~0,2%" == "#!" (goto :goodstart)
echo First line of %pyscript% does not start with "#!"
exit /b 1
:goodstart
set py_exe=%line1:~2%
call %py_exe% %pyscript% %*
"""

class my_install_scripts(install_scripts):
    def run(self):
        install_scripts.run(self)
        if not os.name == "nt":
            return
        for filepath in self.get_outputs():
            # If we can find an executable name in the #! top line of the script
            # file, make .bat wrapper for script.
            with open(filepath, 'rt') as fobj:
                first_line = fobj.readline()
            if not (first_line.startswith('#!') and
                    'python' in first_line.lower()):
                log.info("No #!python executable found, skipping .bat "
                            "wrapper")
                continue
            pth, fname = psplit(filepath)
            froot, ext = splitext(fname)
            bat_file = pjoin(pth, froot + '.bat')
            bat_contents = BAT_TEMPLATE.replace('{FNAME}', fname)
            log.info("Making %s wrapper for %s" % (bat_file, filepath))
            if self.dry_run:
                continue
            with open(bat_file, 'wt') as fobj:
                fobj.write(bat_contents)

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
    cmdclass = {'install_scripts':my_install_scripts},
    long_description = open('README.md').read()
)
