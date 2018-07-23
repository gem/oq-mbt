import sys
import os


def modules_cleaner():
    global gem_cleaner

    ve_path = os.getenv('VIRTUAL_ENV')

    if 'gem_cleaner' not in globals():
        gem_cleaner = sys.modules.copy()
    else:
        for k in list(sys.modules.keys()):
            if sys.modules[k] is None:
                del sys.modules[k]
                continue

            if k not in gem_cleaner:
                if k == 'pkg_resources':
                    del sys.modules[k]
                    continue
                try:
                    # print(sys.modules[k].__file__)
                    if (sys.modules[k].__file__.startswith(ve_path) or
                        sys.modules[k].__file__.startswith(
                            '/usr/lib/')):
                        continue
                    del sys.modules[k]
                except:
                    pass
