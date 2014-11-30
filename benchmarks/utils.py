
import contextlib
import os

@contextlib.contextmanager
def cd(newpath):
    """
    Change the current working directory to `newpath`, temporarily.

    If the old current working directory no longer exists, do not return back.
    """
    oldpath = os.getcwd()
    os.chdir(newpath)
    try:
        yield
    finally:
        try:
            os.chdir(oldpath)
        except OSError:
            # If oldpath no longer exists, stay where we are.
            pass
