from setuptools import setup, find_packages

requires = [
    'scipy',
    'numpy >= 1.2',
    'pydicom >= 0.9.9',
    'matplotlib >= 1.3.0',
    'six >= 1.5',
    'dicompyler-core == 0.5.3',
    'Jinja2',
    'Requests',
    'Tornado == 4.4.2',
    'PyYaml',
    'bokeh == 0.12.6',
    'python-dateutil',
    'psycopg2',
    'fuzzywuzzy',
    'python-Levenshtein',
    'shapely[vectorized] == 1.6b2',
    'freetype-py',
    'statsmodels',
]

setup(
    name='dvh-analytics',
    include_package_data=True,
    packages=find_packages(),
    version='0.1.34',
    description='Create a database of DVHs, views with Bokeh',
    author='Dan Cutright',
    author_email='dan.cutright@gmail.com',
    url='https://github.com/cutright/DVH-Analytics',
    download_url='https://github.com/cutright/DVH-Analytics/archive/master.zip',
    license="MIT License",
    keywords=['dvh', 'radiation therapy', 'research', 'dicom', 'dicom-rt', 'bokeh'],
    classifiers=[],
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'dvh=dvh.__main__:main',
        ],
    },
    long_description="""DVH Database for Clinicians and Researchers
    
    DVH Analytics is a code to help radiation oncology departments build an in-house database of treatment planning 
    data for the purpose of historical comparisons.

    This code builds a SQL database of DVHs and various planning parameters from DICOM files (i.e., Plan, Structure, 
    Dose). Currently, only photon and electron plans have been tested with Philips Pinnacle, however, we intend to 
    accomodate proton and brachytherapy plans as well. Since this code extracts data directly from DICOM files, 
    and we intend to accommodate an array of treatment planning system vendors.
    
    This is a work in progress and just now in testing. Please see our TODO.md on github to see our upcoming improvements.
    """
)