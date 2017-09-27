from os.path import dirname, join
from setuptools import setup, find_packages

with open(join(dirname(__file__), 'autocomment/VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()

setup(
    name='auto-comment',
    version=version,
    url='http://cnets.indiana.edu',
    description='A tool to do auto comment',
    # long_description=open('README.md').read(),
    author='Chengcheng Shao',
    maintainer='Chengcheng Shao',
    maintainer_email='shaoc@indiana.edu',
    license='GPLv3',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'console_scripts': ['autocomment = autocomment.cmdline:main']
    },
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: GPL :: Version 3',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'docopt>=0.6.0',
        'schema',
        'selenium',
        'pyyaml',
    ],)
