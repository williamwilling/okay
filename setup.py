from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='trv-okay',
    version='1.0.0',
    description='A library for validating Python dictionaries.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Joost Ronkes Agerbeek',
    author_email='joost.ronkes@trivago.com',
    packages=find_packages('src'),
    package_dir={ '': 'src' },
    url='https://github.com/trivago/validator',
    project_urls={
        'Documentation': 'https://github.com/trivago/okay/blob/master/docs/README.md',
        'Changelog': 'https://github.com/trivago/okay/blob/master/docs/changelog.md',
        'Issue Tracker': 'https://github.com/trivago/okay/issues'
    },
    keywords=[ 'validation' ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ]
)