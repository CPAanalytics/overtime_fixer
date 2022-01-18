
from setuptools import setup


setup(
    name='overtime_fix',
    version='1',
    packages=['overtime_fix'],
    package_dir ={'overtime_fix': 'overtime_fix'},
    url='',
    license='',
    author='jchevalier',
    author_email='jchevalier@apspayroll.com',
    description='Calculates difference between two csv files',
    install_requires=['Click', 'pandas'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'overtime_fix = overtime_fix.main:overtime_fix',

        ]},
)

if __name__ == 'setup.py':
    setup()

