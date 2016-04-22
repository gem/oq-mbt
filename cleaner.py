import sys


def modules_cleaner():
    global gem_cleaner
    if 'gem_cleaner' not in globals():
        gem_cleaner = sys.modules.copy()
    else:
        for k in list(sys.modules.keys()):
            if k not in gem_cleaner:
                del sys.modules[k]
