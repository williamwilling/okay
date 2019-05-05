import os
import sys

# Make sure the unit tests can find the modules in the src-directory.
test_dir = os.path.dirname(__file__)
root_dir = os.path.split(test_dir)[0]
src_dir = os.path.join(root_dir, 'src')
if src_dir not in sys.path:
    sys.path.append(src_dir)