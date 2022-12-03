import os
from setuptools import setup, find_packages


setup(
    name='syncl2r',
    version='0.0.1',
    py_modules=['syncl2r'],
    keywords=['syncltor', 'syncl2r'],
    author='N0I0C0K',
    author_email='nick131410@aliyun.com',
    url='https://github.com/N0I0C0K/SyncL2R',
    packages=find_packages('./syncl2r'),
    package_dir={'': './syncl2r'},
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': ['syncl2r=syncl2r.syncl2r:main']
    }
)
