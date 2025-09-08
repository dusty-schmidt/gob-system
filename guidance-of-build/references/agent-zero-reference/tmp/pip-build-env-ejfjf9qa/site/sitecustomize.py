
import os, site, sys

# First, drop system-sites related paths.
original_sys_path = sys.path[:]
known_paths = set()
for path in {'/home/ds/miniconda3/envs/gob-core/lib/python3.11/site-packages'}:
    site.addsitedir(path, known_paths=known_paths)
system_paths = set(
    os.path.normcase(path)
    for path in sys.path[len(original_sys_path):]
)
original_sys_path = [
    path for path in original_sys_path
    if os.path.normcase(path) not in system_paths
]
sys.path = original_sys_path

# Second, add lib directories.
# ensuring .pth file are processed.
for path in ['/home/ds/sambashare/gob_agent/tmp/pip-build-env-ejfjf9qa/overlay/lib/python3.11/site-packages', '/home/ds/sambashare/gob_agent/tmp/pip-build-env-ejfjf9qa/normal/lib/python3.11/site-packages']:
    assert not path in sys.path
    site.addsitedir(path)
