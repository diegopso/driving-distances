try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'Driving Distances - JOB',
    'version': '0.1.0',
    'description': 'Pipeline to measure driving distances of vehicles per day.',
    'author': 'Diego Oliveira',
    'url': '--',
    'download_url': '--',
    'author_email': 'diegopso2@gmail.com',
    'install_requires': [
        'numpy', 'pandas', 'python-dotenv', 'osmnx', 'scikit-learn', 'pymysql', 'sqlalchemy'
    ]
}

setup(**config)