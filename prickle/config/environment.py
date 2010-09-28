# Copyright 2010 Dusty Phillips

# This file is part of Prickle.

# Prickle is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.

# Prickle is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General
# Public License along with Prickle.  If not, see
# <http://www.gnu.org/licenses/>.

"""Pylons environment configuration"""
import os

from jinja2 import Environment, FileSystemLoader
from pylons.configuration import PylonsConfig

import prickle.lib.app_globals as app_globals
import prickle.lib.helpers
from prickle.config.routing import make_map

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    config = PylonsConfig()
    
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='prickle', paths=paths)

    config['routes.map'] = make_map(config)
    config['pylons.app_globals'] = app_globals.Globals(config)
    config['pylons.h'] = prickle.lib.helpers
    
    # Setup cache object as early as possible
    import pylons
    pylons.cache._push_object(config['pylons.app_globals'].cache)
    

    # Create the Jinja2 Environment
    jinja2_env = Environment(loader=FileSystemLoader(paths['templates']))
    config['pylons.app_globals'].jinja2_env = jinja2_env

    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
    
    return config
