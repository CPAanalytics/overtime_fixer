import shutil
import os
from configparser import ConfigParser

deployment_path = 'Z:\\overtime_fix\\overtime_fix-1.tar.gz'
setup_path = 'setup.py'

if os.path.exists(deployment_path):
    os.remove(deployment_path)


os.system(f'cmd /c "python {setup_path} sdist"')

shutil.copy('dist\\overtime_fix-1.tar.gz', deployment_path)

