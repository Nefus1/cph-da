import os
from fnmatch import fnmatchcase

from setuptools import find_namespace_packages, setup

standard_exclude = ('*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')


def find_package_data(where='.', package='', exclude=standard_exclude,
                      exclude_directories=standard_exclude_directories):
    """Collect the data/ files (questions, templates, static, sources) for the package."""
    out = {}
    stack = [(os.path.normpath(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                if any(fnmatchcase(name, pat) or fn.lower() == pat.lower() for pat in exclude_directories):
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    stack.append((fn, '', package + '.' + name if package else name))
                else:
                    stack.append((fn, prefix + name + '/', package))
            elif not any(fnmatchcase(name, pat) or fn.lower() == pat.lower() for pat in exclude):
                out.setdefault(package, []).append(prefix + name)
    return out


with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='docassemble.cphda',
    version='0.1.0',
    description='CPH hub of docassemble interviews and document templates for California practice.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='CPH',
    license='Proprietary',
    url='https://github.com/nefus1/cph-da',
    packages=find_namespace_packages(include=['docassemble.*']),
    install_requires=[],
    zip_safe=False,
    package_data=find_package_data(where='docassemble/cphda/', package='docassemble.cphda'),
)
