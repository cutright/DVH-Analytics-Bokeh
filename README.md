# DVH Analytics
<img src='https://cloud.githubusercontent.com/assets/4778878/26684430/99fc183e-46ac-11e7-9e41-b768141212d5.png' align='right' width='300' alt="DVH Analytics screenshot">  
 
DVH Analytics is a code to help radiation oncology departments build an in-house database of treatment planning data 
for the purpose of historical comparisons.  

This code is still in development.  Please contact the developer if  you are interested in testing.

This code builds a SQL database of DVHs and various planning parameters from DICOM files 
(i.e., Plan, Structure, Dose). Currently, only photon and electron plans have been tested with Philips Pinnacle,
however, we intend to accomodate proton and brachytherapy plans as well.  Since this code extracts data
directly from DICOM files, and we intend to accomodate an array of treatment planning system vendors.

This code is built upon these core libraries:
* [pydicom](http://code.google.com/p/pydicom/) - Read, modify and write DICOM files with python code
* [dicompyler-core](https://pypi.python.org/pypi/dicompyler-core) - Extensible radiation therapy research platform and viewer for DICOM and DICOM RT
* [Bokeh](http://bokeh.pydata.org/en/latest/index.html) - Interactive Web Plotting for Python

For installation instructions, see our [installation notes](https://github.com/cutright/DVH-Analytics/blob/master/install_notes.md).

## Dependencies
* [Python](https://www.python.org) 2.7 tested  
    * Python 3 not currently supported
* [PostgreSQL](https://www.postgresql.org/) and [psycopg2](http://initd.org/psycopg/)
* [scipy](https://scipy.org)
    * [numpy](https://pypi.python.org/pypi/numpy) 1.12.1 tested
* [pydicom](https://github.com/darcymason/pydicom) 0.9.9
* [fuzzy wuzzy](https://github.com/seatgeek/fuzzywuzzy) 0.15
* [dicompyler-core](https://pypi.python.org/pypi/dicompyler-core) 0.5.3
    * requirements per [developer](https://github.com/bastula)
        * [numpy](http://www.numpy.org/) 1.2 or higher
        * [pydicom](http://code.google.com/p/pydicom/) 0.9.9 or higher
            * pydicom 1.0 is preferred and can be installed via pip using: pip install https://github.com/darcymason/pydicom/archive/master.zip
        * [matplotlib](http://matplotlib.sourceforge.net/) 1.3.0 or higher (for DVH calculation)
        * [six](https://pythonhosted.org/six/) 1.5 or higher
* [Bokeh](http://bokeh.pydata.org/en/latest/index.html) 0.12.6
    * requirements per [developer](http://bokeh.pydata.org/en/latest/docs/installation.html)
        * [NumPy](http://www.numpy.org/)
        * [Jinja2](http://jinja.pocoo.org/)
        * [Six](https://pythonhosted.org/six/)
        * [Requests](http://docs.python-requests.org/en/master/user/install/)
        * [Tornado](http://www.tornadoweb.org/en/stable/) >= 4.0, <=4.4.2
        * [PyYaml](https://pypi.python.org/pypi/pyaml)
        * [DateUtil](https://pypi.python.org/pypi/python-dateutil)
