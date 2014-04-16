from distutils.core import setup

setup(name='mlb-data',
    version='0.1',
    license='Apache 2.0',
    description='Tools for manipulating the data from the major sources of MLB data',
    author='Sean Kelly',
    author_email='',
    url='https://github.com/seankelly/mlb-data',
    packages=['mlb'],
    scripts=[
            'bin/dump-bip',
            'bin/dump-pitches',
            'bin/fetch-gameday-data',
            'bin/find-homeplate',
            'bin/generate-cards',
            'bin/parse-gameday-xml',
            'bin/parse-retrosheet-games',
            'bin/summarize-retrosheet',
        ],
    requires=['sqlalchemy', 'requests', 'lxml'],
    )
