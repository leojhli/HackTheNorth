"""Import the user-supplied Make export, rejecting unsafe archive paths."""
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

archive = Path(r'C:\Users\Mathe\Downloads\BeProgram.zip')
target = Path('apps/dashboard').resolve()
with ZipFile(archive) as z:
    for entry in z.infolist():
        name = PurePosixPath(entry.filename)
        if name.is_absolute() or '..' in name.parts or '\\' in entry.filename or ':' in entry.filename:
            raise ValueError('Unsafe archive path')
        if entry.file_size > 20_000_000:
            raise ValueError('Unexpectedly large export entry')
        dest = (target / str(name)).resolve()
        if not dest.is_relative_to(target):
            raise ValueError('Archive leaves target')
        if entry.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(z.read(entry))
print('Imported Figma source into', target)
