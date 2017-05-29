from distutils.core import setup

setup(
    name='dvh-analytics',
    packages=['dvh-analytics'],
    version='0.0.1',
    description='Create a SQL database of DVHs',
    author='Dan Cutright',
    author_email='dan.cutright@gmail.com',
    url='https://github.com/cutright/DVH-Analytics',
    download_url='https://github.com/cutright/DVH-Analytics/archive/master.zip',
    license="MIT License",
    keywords=['dvh', 'radiation therapy', 'research', 'dicom', 'dicom-rt'],
    classifiers=[],
    long_description="""
    DVH Analytics is a code to help radiation oncology departments build an in-house database of treatment planning 
    data for the purpose of historical comparisons.

    This code builds a SQL database of DVHs and various planning parameters from DICOM files (i.e., Plan, Structure, 
    Dose). Currently, only photon and electron plans have been tested with Philips Pinnacle, however, we intend to 
    accomodate proton and brachytherapy plans as well. Since this code extracts data directly from DICOM files, 
    and we intend to accomodate an array of treatment planning system vendors.
    """
)