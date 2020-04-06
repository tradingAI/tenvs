import codecs
import os

from setuptools import find_packages, setup


def read(fname):
    return codecs.open(os.path.join(
        os.path.dirname(__file__), fname)).read().strip()


with open("README.md", "r") as fh:
    long_description = fh.read()


def read_install_requires():
    reqs = [
            'beautifulsoup4',
            'gym',
            'lxml>=3.8.0',
            'matplotlib==3.1.3',
            'msgpack>=0.5.6',
            'numpy==1.16.0',
            'pandas==0.25.3',
            'pyzmq>=16.0.0',
            'requests>=2.0.0',
            'scipy',
            'simplejson>=3.16.0',
            'tushare']
    return reqs


setup(name='tenvs',
      version=read('tenvs/VERSION.txt'),
      description='',
      url='https://github.com/tradingAI/tenvs',
      author='liuwen',
      author_email='liuwen.w@qq.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
      python_requires='>=3',
      install_requires=read_install_requires(),
      )
