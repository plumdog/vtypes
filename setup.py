from setuptools import setup


setup(
    name='vtypes',
    packages=['vtypes'],
    version='0.0.1',
    author='Andrew Plummer',
    author_email='plummer574@gmail.com',
    url='https://github.com/plumdog/vtypes',
    description=' For coercing dicts of types, eg requests to and responses from a JSON api.',
    test_suite='tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Operating System :: OS Independent',
    ])
