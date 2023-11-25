try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='summary-extraction',
    version='0.3',
    author='Alexandru Stanciu',
    author_email='alexandru.stanciu@gmail.com',
    packages=['summary'],
    include_package_data=True,
    license='LICENSE.txt',
    url='https://github.com/svven/summary',
    # download_url = 'https://github.com/svven/summary/tarball/0.3',
    description='Extract the title, image and description from any URL.',
    long_description=open('README.md').read(),
    install_requires=[        
        'adblockparser',
        'extraction', # git+https://github.com/svven/extraction.git@master#egg=extraction
        # 'Jinja2' # for rendering
        'lxml',
        'Pillow',
        'requests',
        'requests-html',
        'urltools',
        'w3lib',
    ],
)
