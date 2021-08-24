from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='okay-validator',
    version='2.0.1',
    description='A library for validating Python dictionaries.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Joost Ronkes Agerbeek',
    author_email='joost@ronkes.nl',
    packages=find_packages('src'),
    package_dir={ '': 'src' },
    url='https://github.com/williamwilling/okay',
    project_urls={
        'Documentation': 'https://github.com/williamwilling/okay/blob/master/docs/README.md',
        'Changelog': 'https://github.com/williamwilling/okay/blob/master/docs/changelog.md',
        'Issue Tracker': 'https://github.com/williamwilling/okay/issues'
    },
    keywords=[ 'validation' ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries'
    ]
)