#! /usr/bin/env python

from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='ChampEdx',
      version='0.1',
      description='Code for reading TICRA CHAMP .edx files',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Data Processing :: Electromagnetics',
      ],
      keywords='CHAMP TICRA file feedhorn radiation pattern',
      url='http://github.com/pgrimes',
      author='Paul Grimes',
      author_email='pgrimes@cfa.harvard.edu',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'lxml',
          'numpy',
          'matplotlib'
          #'NumpyUtility'
      ],
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
