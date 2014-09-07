try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='summary-extraction',
    version='0.2',
    author='Alexandru Stanciu',
    author_email='alexandru.stanciu@gmail.com',
    packages=['summary'],
    license='LICENSE.txt',
    url='https://github.com/svven/summary',
    # download_url = 'https://github.com/svven/summary/tarball/0.2',
    description='Extract the title, image and description from any URL.',
    long_description=open('README.rst').read(),
    install_requires=[
        'Pillow >= 2.4.0',
        'adblockparser >= 0.2',
        'extraction >= 0.2',
        'lxml >= 3.3.5',
        # 're2 >= 0.2.20',
        'requests >= 2.2.1',
        'w3lib >= 1.6',
    ],
)