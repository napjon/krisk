from setuptools import setup, find_packages
from krisk import __version__

setup(
    name='krisk',
    version=__version__,
    description='Echarts Statistical Visualization for Python Data Science',
    author='Jonathan Napitupulu',
    author_email='napitupulu.jon@gmail.com',
    download_url='https://github.com/napjon/krisk/',
    url='https://github.com/napjon/krisk/',
    license='BSD (3-clause)',
    packages=find_packages(),
    package_data={'krisk': ['static/*.html',
                            'static/*.js']},
    classifiers=[
        'Development Status :: 4 - Beta', 'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.5'
    ])



