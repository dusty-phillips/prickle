This is a simple time tracking app inspired by Freckle. Currently it just logs times for a given day, without so much as a total. Its primary purpose is for me to study Pylons and CouchDB, so I doubt it's of much interest to you. It doesn't even support user auth.

Installation and Setup
======================


Ok, these are generic instructions, as a placeholder. The proper setup procedure will require creating a virtual environment, git cloning something, and installing a bunch of stuff from a pip requirements file or something.

Install ``prickle`` using easy_install::

    easy_install prickle

Make a config file as follows::

    paster make-config prickle config.ini

Tweak the config file as appropriate and then setup the application::

    paster setup-app config.ini

Then you are ready to go.
