import sys
sys.path.insert(0,"/var/www/iiiscience")

import logging
logging.basicConfig(stream=sys.stderr)

from Controller import app as application
