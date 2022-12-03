import pathlib

pa = pathlib.PurePath('c:/a/a/ab')
pb = pathlib.PurePath(pa, './a.py')
print(pb)
