import os
import sys

path = "/home/virtual/vps-cbced9/a/a588fe7474/stream"
if path not in sys.path:
    sys.path.append(path)

from stream.wsgi import application
