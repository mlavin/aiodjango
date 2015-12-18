import ast
import codecs
import os
from setuptools import setup, find_packages


class VersionFinder(ast.NodeVisitor):

    def __init__(self):
        self.version = None

    def visit_assign(self, node):
        if node.targets[0].id == '__version__':
            self.version = node.value.s


def read(*parts):
    """Read a file into a string"""
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as f:
        return f.read()


def get_package_meta():
    version = VersionFinder()
    parsed = ast.parse(read('aiodjango', '__init__.py'))
    version.visit(parsed)
    return {
        '__version__': version.version,
        '__doc__': ast.get_docstring(parsed),
    }

_meta = get_package_meta()


setup(
    name='aiodjango',
    version=_meta['__version__'],
    author='Mark Lavin',
    author_email='markdlavin@gmail.com',
    packages=find_packages(exclude=['example']),
    include_package_data=True,
    url='https://github.com/mlavin/aiodjango',
    license='BSD',
    description=' '.join(_meta['__doc__'].splitlines()).strip(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    long_description=read('README.rst'),
    install_requires=[
        'aiohttp>=0.19.0',
        'aiohttp-wsgi>=0.3.0',
    ],
    test_suite='runtests.runtests',
)
