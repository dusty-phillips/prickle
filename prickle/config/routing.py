"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False
    map.explicit = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE

    map.connect('/timesheet/date/{date}', controller="timesheet",
            action="date", requirements={'date': '\d\d\d\d-\d\d-\d\d'})
    map.connect('/timesheet/month/{year}/{month}', controller="timesheet",
            action="month", requirements={'year': '\d\d\d\d', 'month': '\d\d'})

    map.connect('/{controller}/{action}')
    map.connect('/{controller}/{action}/{id}')

    map.connect('/', controller='timesheet', action='index')

    return map
