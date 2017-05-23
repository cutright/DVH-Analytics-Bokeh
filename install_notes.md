# Installation notes for DVH Analytics

## Pre-requisites:
 - Chrome or Firefox
 - PostgreSQL (tested with 9.6)
 - Python 2.7 (python3 not supported)
 - pip (python package manager)

## Setting up your python environment
 - Download the entire source code from Github either via git or manual download.
   - Be sure command line tools are installed if on Mac OS. See [Additional Notes](#additional-notes).
 - From a terminal window, change your directory to the DVH-Analytics folder.
 - execute the install script by typing the following from the project directory in a terminal:
~~~~
pip install -r requirements.txt
~~~~


## Processing test files
From the same directory as the previous step, type the following:
python dvh/dicom_to_sql.py

This will take several minutes. This python code will process all dicom files located in the inbox as specified
in the file dvh/preferences/import_settings.txt and move them into the location specified by 'imported' in the
same file.


## Web view
From the same directory as the previous step, type the following to start the bokeh server:
bokeh serve --show dvh/
If Chrome or Firefox is not your default browswer, you'll need to copy and paste the url into Chrome or Firefox.
From within the active terminal, press ctrl + c to stop the Bokeh server.

If you would like to specify an IP or port other than the default 127.0.0.1:5006, use the following when starting
the bokeh server.  You may be interested in this if running from a computer with a static IP and would like
to access this bokeh server from across your network.
~~~~
bokeh serve --allow-websocket-origin=<new IP:port> dvh/
~~~~
~~~~
bokeh serve dvh/ --port <some other port number>
~~~~

----------------------------------------------------------------------------------------------
## Additional Notes

### Python 2.7 (Windows only, Xcode command line tools for mac and Ubuntu both include Python 2.7)
Download Python 2.7 (not 3.x) from:  
https://www.python.org/downloads/windows/

 - After the installation is complete, you'll need to edit your environment to include python in the command prompt.
 - Open a Windows Explorer.
   - Right-click on My Computer.
   - Click Properties -> Advanced system settings -> Environment variables
 - Create a new System variables
   - Variable name: PYTHONPATH
   - Variable value: C:\Python27\Lib;C:\Python27\DLLs;C:\Python27\Lib\lib-tk
 - Then edit the system variable Path by appending the following to the end of whatever is already there:
   - ;%PYTHONPATH%

Now you should be able to type 'python' in your command line (cmd.exe) to get a python console. If this doesn't work,
you'll need to investigate why python did not install or is not found in your command line.  If this worked, exit by
typing exit() and pressing enter.


### Xcode Command Line Tools (Mac Only)
Make sure Xcode command line tools are installed
If the full Xcode package is installed (from the Mac App Store), entire the following into a terminal window:
xcode-select --install


### PostgreSQL
If you are familiar with PostgreSQL and have access to a PostgreSQL DB, you simply need to fill in the
login information in:
*dvh/preferences/sql_connection.cnf*.

If you need PostgreSQL, here are some options for each OS

#### Mac OS:
Simply download the PostgreSQL app: http://postgresapp.com/  
 - Open the app
 - Click "Start"
 - Double-click "postgres" with the cylindrical database icon
 - Type the following in the SQL terminal:
~~~~
create database dvh;
~~~~
Then quit by typing:
~~~~
\q
~~~~

NOTE: You may replace dvh with any database name you wish, but you must update dbname in
dvh/preferences/sql_connection.cnf to reflect what database name you chose.
This app must be running when writing or accessing data.

If you use OS authentication, make sure dvh/preferences/sql_connection.cnf does not have 'user' or 'password' names.
If you choose to create a user and password, update said .cnf file appropriately.

#### Ubuntu
Type the following in a terminal:
~~~~
sudo apt-get install postgresql postgresql-client postgresql-contrib libpq-dev
sudo apt-get install pgadmin3
~~~~
Upon successful installation, open type 'pgadmin3' in the terminal to open the graphical admin.
 - Create a user and database of your choice (same instructions found below for Windows)
 - Update dvh/preferences/sql_connection.cnf as appropriate.

#### Windows
Download the installer for BigSQL: https://www.bigsql.org/postgresql/installers.jsp/

 - Be sure to include pgAdmin3 LTS
 - After installation, launch pgAdmin3 LTS from the Windows Start Menu.
   - Right-click localhost and then click connect.
   - Right-click Login Roles and then click New Login Role.
   - Fill in Role name (e.g., dvh), click OK
   - Right-click Databases then click New Database
   - Fill in Name (e.g., dvh), set owner to the Role name you just created. Click OK.


### PIP (python package management):
From a terminal window, type:

*Mac*
~~~~
easy_install pip
~~~~

*Ubuntu*
~~~~
sudo apt-get install python-pip
~~~~

*Windows*  
Download get-pip.py from here: https://pip.pypa.io/en/stable/installing/  
Then compile:
~~~~
python get-pip.py
~~~~