from setuptools import setup, find_packages

setup(
    name='compiler_design',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
)
