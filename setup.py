from setuptools import setup, find_packages
from pathlib import Path
from syncl2r import version


def load_requirements(fname: str):
    pf = Path(fname)
    return pf.read_text(encoding="utf-8").split("\n")


setup(
    name="syncl2r",
    version=version,
    py_modules=["syncl2r"],
    packages=find_packages(),
    author="N0I0C0K",
    author_email="nick131410@aliyun.com",
    url="https://github.com/N0I0C0K/SyncL2R",
    install_requires=load_requirements("./requirements.txt"),
    entry_points={
        "console_scripts": ["syncl2r=syncl2r:entry_point", "sync=syncl2r:entry_point"]
    },
)
