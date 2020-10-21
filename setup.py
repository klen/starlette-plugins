import re
from os import path as op

from setuptools import setup


def _read(fname):
    try:
        return open(op.join(op.dirname(__file__), fname)).read()
    except IOError:
        return ''


meta = _read('starlette_plugins.py')

setup(
    name='starlette-plugins',
    version=re.search(r'^__version__\s*=\s*"(.*)"', meta, re.M).group(1),
    license=re.search(r'^__license__\s*=\s*"(.*)"', meta, re.M).group(1),
    description="Create Starlette Plugins easier",
    long_description=_read('README.rst'),

    py_modules=['starlette_plugins'],

    author='Kirill Klenov',
    author_email='horneds@gmail.com',
    homepage="https://github.com/klen/starlette-plugins",
    repository="https://github.com/klen/starlette-plugins",
    keywords="starlette plugins",

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        "Topic :: Software Development :: Libraries",
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)

