import pathlib

pa = pathlib.PurePath('c:/a/a/ab')
print((pa/'*').as_posix())
