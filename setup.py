from setuptools import setup, find_packages


setup(
    name='syncl2r',
    version='0.0.1',
    py_modules=['syncl2r'],
    keywords=['syncl2r'],
    author='N0I0C0K',
    author_email='nick131410@aliyun.com',
    url='https://github.com/N0I0C0K/SyncL2R',
    packages=['syncl2r'],
    entry_points={
        'console_scripts': ['syncl2r=syncl2r:main']
    }
)
