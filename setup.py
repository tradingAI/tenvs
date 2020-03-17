from setuptools import find_packages, setup

setup(name='tenvs',
      version='0.0.1',
      description='',
      url='https://github.com/iminders/tenvs',
      author='iminders',
      author_email='liuwen.w@qq.com',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['gym', 'tushare']
      )
