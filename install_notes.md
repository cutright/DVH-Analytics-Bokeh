# Installation notes for DVH Analytics

## Pre-requisites:
 - [Chrome](https://www.google.com/chrome/browser/desktop/) or [Firefox](https://www.mozilla.org/en-US/firefox/new/)
 - [PostgreSQL](https://www.postgresql.org/) (tested with 9.6)
 - [Python 2.7](https://www.python.org/downloads/release/python-2712/) (python3 not supported)
 - [pip](https://pip.pypa.io/en/stable/installing/) (python package manager)
 - Xcode Command Line Tools (Mac only)  

If any of these are not installed, see [Additional Notes](#additional-notes).  

## Setting up your python environment
DVH Analytics is available via pip install:
~~~~
$ pip install dvh-analytics
~~~~
If you're on Mac or Linux, you may need:
~~~~
$ sudo pip install dvh-analytics
~~~~

## Define directories and connection settings
For a web-based UI, type in the following to access the Settings:
~~~~
$ dvh setup
~~~~
or the following for a command-line based setup:
~~~~
$ dvh setup_simple
~~~~

## Processing test files
To verify all of your settings are valid and installation was successful, type:
~~~~
$ dvh test
~~~~
This will process all dicom files located in the test files folder. If this test passes, then all dependencies are 
successfully installed (e.g., PostgreSQL, Python libraries), import directories are valid, and communication with your 
SQL DB has been established.

## Importing your own data
To import your own data, you can click "Import all from inbox" in the Database Editor tab of the 
[settings GUI](#ROI-Name-Manager,-DB Editor,-and-Backup-&-Restore)

Alternatively, to import your own data via command line for more options:
~~~~
$ dvh import
~~~~
Assuming all of the previous steps were successful, all dicom files anywhere within your inbox will be imported 
into the SQL database, then organized by patient name and moved to the specified imported folder.  Note that by 
default, the code will not import dicom files with Study Instance UIDs that are already in the database.  You 
may over-ride any of these default behaviors with any combination of the following optional flags:
 - force-update
 - do-not-organize
 - do-not-move  
 
For example, the following command will not check for duplicate database entries and will not remove the dicom files 
from the inbox folder:
~~~~
$ dvh import --force-update --do-not-move-files
~~~~
If you'd like to import from a directory other than the one in your settings:
~~~~
$ dvh import --start-path /someabsolute/directory/name
~~~~
## ROI Name Manager, DB Editor, and Backup & Restore
Using the 'settings' command will start a Bokeh server and open your default browser to access the ROI Name 
Manager, DB Editor, and Backup & Restore modules.  Be sure to stop the server when you're done by press ctrl + c 
in the command line window.
~~~~
$ dvh admin
~~~~
## Main DVH Analytics view
Type the following to start the Bokeh server:  
~~~~
$ dvh run
~~~~
If Chrome or Firefox is not your default browswer, you'll need to copy and paste the url into Chrome or Firefox.
From within the active terminal, press ctrl + c to stop the Bokeh server.

If you would like to specify an IP or port other than the default 127.0.0.1:5006, use the following when starting
the Bokeh server.  You may be interested in this if you are running from a computer with a static IP and would like
to access this Bokeh server from across your network.
~~~~
$ dvh run --allow-websocket-origin <new IP:port>
~~~~
~~~~
$ dvh run --port <some other port number>
~~~~
These two features work with any of the commands that start web-based UI.

----------------------------------------------------------------------------------------------
## Additional Notes

### Python 2.7  
*(Windows only, Xcode command line tools for mac and Ubuntu both include Python 2.7)*  
Download Python 2.7 (not 3.x) from: https://www.python.org/downloads/windows/

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
If the full Xcode package is installed (from the Mac App Store), enter the following into a terminal window:
~~~~
$ xcode-select --install
~~~~

### PostgreSQL
If you are familiar with PostgreSQL and have access to a PostgreSQL DB, you simply need to fill in the
login information by running:
~~~
$ dvh settings --sql
~~~

If you need PostgreSQL, here are some options for each OS.

*Mac OS*  
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

NOTE: You may replace dvh with any database name you wish, but you must update dbname in settings to reflect what 
database name you chose.  

*Ubuntu*  
Type the following in a terminal:
~~~~
$ sudo apt-get install postgresql postgresql-client postgresql-contrib libpq-dev
$ sudo apt-get install pgadmin3
~~~~
Upon successful installation, open type 'pgadmin3' in the terminal to open the graphical admin.  
Then, create a user and database of your choice (same instructions found below for Windows)

*Windows*  
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
$ easy_install pip
~~~~

*Ubuntu*
~~~~
$ sudo apt-get install python-pip
~~~~

*Windows*  
Download get-pip.py from here: https://pip.pypa.io/en/stable/installing/  
Then compile:
~~~~
$ python get-pip.py
~~~~
