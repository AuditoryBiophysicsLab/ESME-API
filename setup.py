from setuptools import setup, find_packages

setup(
    name='esme',
    packages=find_packages(),
    url='https://esme.bu.edu',
    entry_points={
        'console_scripts': [
            'esme = esme.__main__:main'
        ]
    },
    license='MPL 2.0',
    setup_requires=['vcversioner'],
    vcversioner={'version_module_paths': ['esme/_version.py'],
                 },
    author='Graham Voysey',
    author_email='gvoysey@bu.edu',
    description='A python API for reading ESME Workbench simulation results',
    install_requires=['attrs>=17.4.0']
)
