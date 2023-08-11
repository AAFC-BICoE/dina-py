from setuptools import setup, find_packages

setup(
    name='dina-web-api',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'marshmallow-jsonapi',
        'keycloak',
        'PyYAML',
    ],
    author='AAFC-BICoE',
    # author_email='your@email.com',
    description='Dina Web Services - Python library for interacting with the DINA web services',
    # long_description='Long description of your package',
    # long_description_content_type='text/markdown',
    url='https://github.com/AAFC-BICoE/dina-py',
)
