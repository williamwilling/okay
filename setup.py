from setuptools import setup, find_packages

setup(
    name='trv_okay',
    version='0.0.1',
    description='A library for validating Python dictionaries.',
    author='Joost Ronkes Agerbeek',
    author_email='joost.ronkes@trivago.com',
    packages=find_packages('src'),
    package_dir={ '': 'src' }
)