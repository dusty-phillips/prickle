try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='prickle',
    version='0.2',
    description='A simple couchdb based time-tracking tool',
    author='Dusty Phillips',
    author_email='dusty@archlinux.ca',
    url='',
    install_requires=[
        "Pylons>=1.0",
        "Jinja2",
        "CouchDB",
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'prickle': ['i18n/*/LC_MESSAGES/*.mo']},
    #message_extractors={'prickle': [
    #        ('**.py', 'python', None),
    #        ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = prickle.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
