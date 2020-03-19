from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(name='tenvs',
      version='1.0.0',
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
      install_requires=[]
      )
