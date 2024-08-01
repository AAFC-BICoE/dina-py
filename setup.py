from setuptools import setup, find_packages

# REQUIREMENTS
with open('requirements.txt', 'r') as req:
    REQUIREMENTS = [line.rstrip() for line in req.readlines() if len(line) > 1 and line[1] != '#']

setup(
    name='dinapy',
    version='0.1.0',
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    author='AAFC-BICoE',
    # author_email='your@email.com',
    description='Dina Web Services - Python library for interacting with the DINA web services',
    # long_description='Long description of your package',
    # long_description_content_type='text/markdown',
    url='https://github.com/AAFC-BICoE/dina-py',
)
