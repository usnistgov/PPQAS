from setuptools import setup

setup(
    name='policy_study',
    version='0.1.1',
    description="",
    install_requires=[
	'Flask>=0.10',
        'xmltodict',
        'pymongo',
        'Flask-WTF',
        'Flask-Login',
        'Flask-Mail',
        'wtforms>=1.0.5,<2.0',
        'pytest',
        'docopt',
        'datadiff'
	],
)
