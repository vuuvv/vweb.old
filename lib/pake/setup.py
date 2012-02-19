from distutils.core import setup
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES
import os
import sys

python_exe = os.path.join(sys.prefix, "python.exe")
pake_bat = '"%s" "%s"' % (python_exe, os.path.join(sys.prefix, "Scripts", "pake"))
pake = """#!%s
from pake.application import Application
Application().run()
""" % python_exe

def create_pake_bat():
	filename = os.path.join("bin", "pake.bat")
	f = open(filename, "w")
	f.write(pake_bat)
	f.close()

def create_pake():
	filename = os.path.join("bin", "pake")
	f = open(filename, "w")
	f.write(pake)
	f.close()

if not os.path.isdir('bin'):
	os.mkdir('bin')
create_pake_bat()
create_pake()

setup(
	name = "Pyake",
	version = "0.0.1",
	url = 'https://github.com/vuuvv/pake',
	author = 'Vuuvv Software Foundation',
	author_email = 'vuuvv@qq.com',
	description = 'A simple python build program with capabilities similar to make.',
	download_url = 'http://media.djangoproject.com/releases/1.3/Django-1.3.1.tar.gz',
	packages = ["pake", "pake.builtins"],
	scripts = ['bin/pake', 'bin/pake.bat'],
	classifiers = ['Development Status :: 2 - Pre-Alpha',
				   'Environment :: Console',
				   'Intended Audience :: Developers',
				   'License :: OSI Approved :: BSD License',
				   'Operating System :: OS Independent',
				   'Programming Language :: Python',
				   'Programming Language :: Python :: 2.6',
				   'Programming Language :: Python :: 2.7',
				   'Topic :: Software Development :: Build Tools',
				   ],
)
