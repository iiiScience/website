import sys
sys.path.insert(0,"/var/www/iiiscience/iiiscience")

import logging
logging.basicConfig(stream=sys.stderr)

from iiiscience.Controller import app as application
