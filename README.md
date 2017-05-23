# DVH Analytics
DVH Database Manager and Viewer

This code is intended for Radiation Oncology departments to build a SQL database of DVH's and various planning parameters from DICOM files (Plan, Structure, Dose).


For installation instructions, see install_notes.txt


## To Do List
### Higher Priorities

- [X] Design install script for a venv
    - [X] Mac
    - [ ] Ubuntu
    - [ ] Windows

- [X] Add ability to plot a temporary plan not in the SQL DB
    - [ ] Design new app for plan review

### Lower Priorities

- [ ] Validate dicompyler-core DVH calculations

- [ ] Validate EUD calculations

- [ ] Write DICOM pre-import validation function

- [ ] Add thorough comments throughout all code

- [ ] Incorporate BED, TCP, NTCP calculations

- [ ] Track wedge info on 3D beams

- [X] Look into filtering by date range
    - [ ] Clean text representation in text field

- [ ] Design UI for backend management

- [ ] Combine data and stats into one ColumnDataSource so endpoints are calculated for stats


## Dependencies
* [Python](https://www.python.org) 2.7 tested
* [PostgreSQL](https://www.postgresql.org/) and [psycopg2](http://initd.org/psycopg/)
* [numpy](https://pypi.python.org/pypi/numpy) 1.12.1 tested
* [pydicom](https://github.com/darcymason/pydicom) 0.9.9
* [dicompyler-core](https://pypi.python.org/pypi/dicompyler-core) 0.5.2
    * requirements per [developer](https://github.com/bastula)
        * [numpy](http://www.numpy.org/) 1.2 or higher
        * [pydicom](http://code.google.com/p/pydicom/) 0.9.9 or higher
            * pydicom 1.0 is preferred and can be installed via pip using: pip install https://github.com/darcymason/pydicom/archive/master.zip
        * [matplotlib](http://matplotlib.sourceforge.net/) 1.3.0 or higher (for DVH calculation)
        * [six](https://pythonhosted.org/six/) 1.5 or higher
* [Bokeh](http://bokeh.pydata.org/en/latest/index.html) 0.12.5
    * requirements per [developer](http://bokeh.pydata.org/en/latest/docs/installation.html)
        * [NumPy](http://www.numpy.org/)
        * [Jinja2](http://jinja.pocoo.org/)
        * [Six](https://pythonhosted.org/six/)
        * [Requests](http://docs.python-requests.org/en/master/user/install/)
        * [Tornado](http://www.tornadoweb.org/en/stable/) >= 4.0, <=4.4.2
        * [PyYaml](https://pypi.python.org/pypi/pyaml)
        * [DateUtil](https://pypi.python.org/pypi/python-dateutil)
