import codecs
import os

from setuptools import find_packages, setup


def read(fname):
    return codecs.open(os.path.join(
        os.path.dirname(__file__), fname)).read().strip()


with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

REQUIRES_PYTHON = ">=3.5.0"


def read_install_requires():
    reqs = [
        'beautifulsoup4',
        'coveralls',
        'flake8',
        'gym',
        'lxml',
        'msgpack',
        'numpy',
        'pytest',
        'pytest-cov',
        'PyYAML',
        'pandas',
        'requests',
        'scipy',
        'simplejson',
        'tushare']
    return reqs


setup(
    name='tenvs',
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

    python_requires=REQUIRES_PYTHON,
    install_requires=read_install_requires(),
    package_data={'': ['*.csv', '*.txt']},
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'License :: OSI Approved :: MIT License',
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 1 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
