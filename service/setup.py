try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'Driving Distances - Web Service',
    'version': '0.1.0',
    'description': 'REST end-point to serve driving distances of vehicles per day.',
    'author': 'Diego Oliveira',
    'url': '--',
    'download_url': '--',
    'author_email': 'diegopso2@gmail.com',
    'install_requires': [
        'Flask', 'pymysql', 'sqlalchemy', 'python-dotenv'
    ]
}

setup(**config)