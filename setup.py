from setuptools import find_packages
from setuptools import setup

MAJOR_VERSION = '1'
MINOR_VERSION = '1'
MICRO_VERSION = '7'
VERSION = "{}.{}.{}".format(MAJOR_VERSION, MINOR_VERSION, MICRO_VERSION)

setup(name='django_json_api',
      version=VERSION,
      description="Streamline JSON API function wrappers for your django app.",
      author='Luke Dupin',
      url='https://github.com/lukedupin/django_json_api',
      author_email='orbital.sfear@gmail.com',
      install_requires=[
          'tox', 'pytest', 'sh'
      ],
      entry_points={
          'console_scripts': ['django_json_api = django_json_api.__main__:main']
      },
      classifiers=[
          'Intended Audience :: Developers',
          'Intended Audience :: Customer Service',
          'Intended Audience :: System Administrators',
          'Operating System :: Microsoft',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration',
          'Topic :: Utilities'
      ],
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      platforms='any')
