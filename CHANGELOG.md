# Change log of DVH Analytics

### 0.5.0 (TBD)
* New ROI Name Manger layout
    * plot now displays entire physician roi map
    * you can show all data or filter institutional rois by linked, unlinked, or branched
* Previously, importing a ROI Map automatically added institutional rois to physician rois.  This behavior has been 
removed.  Adding a new physician will still create a default list of physician rois based on the insitutional roi 
list.  The DEFAULT physician will include only institutional rois
* Functionality added to merge one physician roi into another

### 0.4.10 (2019.1.1)
* Bad reference to SQL config settings in the Ignore DVH button of the ROI Name Mangaer of the Admin view

### 0.4.9 (2019.1.1)
* Organize modules in tools directory
* Generalize update_all_in_db functions in database_editor.py
* ensure all options read from custom options file if available
* Backup tab functionality in Admin view was incomplete since modularization of bokeh views
    * Backup selection menus now update
    * Backup preferences works again

### 0.4.8 (2018.12.27)
* Reorganize python files into directories:
    * path updated with: import update_sys_path
    * columns.py and custom_titles.py now have code wrapped in a class
    * Multiple simultaneous sessions enabled again by wrapping all bokeh objects into classes
* Remove test files
* Catch keyboard interrupt in \_\_main\_\_.py for graceful shutdown
* Moved import_warning_log.txt to user's data directory
* All preferences stored in user folder now so that there's no need to run servers with sudo
* May need to copy files from <script-dir>/preferences into ~/Apps/dvh_analytics/preferences/
* Data directory defaults to ~/Apps/dvh_analytics/data but can still be customized
* All sql/preference backups stored in ~/Apps/dvh_analytics/data/backup now (can't customize)
* options.py now contains imports (os and paths.py)
    * This broke load_options, code added to ignore ModuleType
* Automatically update uncategorized variations in ROI Manager after importing data, updating database, deleting data, 
or reimporting database

### 0.4.7 (2018.12.6)
* Move csv creation to python for less javascript (download.js)
* Some bug catches if certain fields are too long to import into its SQL column
* ROI Name Manager in the Admin view displays a table of the currently saved ROI Map of the 
currently selected physician

### 0.4.697 (2018.11.11) - _removed from PyPi_
* The docker compose file for DVH Analytics Docker had a bug such that it would not share import and sql connection settings between 
main, admin, and settings views.  A directory was created to share changes with each server.
* DVH Analytics will detect if you're using Docker and have docker applicable default sql connection settings
* Note that DVH Analytics Docker has only been validated on Mac

### 0.4.62 & 0.4.68 (2018.11.11) - _removed from PyPi_
* If a RT Plan that is incompatible with the current version of dicom_mlc_analyzer.py, DVH Analytics would crash. 
Now the command prompt will print the failed RT Plan file, and skip the MLC Analyzer tab update, preventing a crash.
* Moving to the bokeh_components directory caused relative import errors. As a temporary fix, all python files moved 
to main dvh directory. This version was verified to work via pip install (and subsequently running with dvh command 
calling \_\_main\_\_.py for entry point), as well as in docker.
* These versions were explicitly tested by running source code with direct bokeh serve calls, pip install of 
DVH Analytics, and using docker-compose.

### 0.4.6 (2018.11.6)
* MAJOR restructuring with majority of main.py moved into bokeh_components directory
    * Next release will begin working on better efficiency
* Residual chart added to Regression tab, will develop into Control Chart
* Begin making code more concise using classes and dictionaries
* Issue #42 - Regression drop-downs not updating properly when deleting/changing EP
* MLC Analyzer does not cause crash if DICOM plan file cannot be found

### 0.4.5 (scrapped)

### 0.4.4b, 0.4.4.4c, 0.4.4.1 (2018.11.1)
* Minor tweaks for on compliance with DICOM files from http://www.cancerimagingarchive.net/
* Move Files Check box added in admin view if user wishes to keep files in the inbox

### 0.4.4a (2018.11.1)
* Minor tweak to check for TPS Vendor tags prior to accessing, working on compliance with DICOM files from 
http://www.cancerimagingarchive.net/

### 0.4.4 (2018.08.15)
* typo in keyword for parameter in dicom_to_sql (import_latest_plan_only changes to import_latest_only)
* Shapely speedups enabled, if available
    * Shapely has calcs available in C, as opposed to C++
* centroid, dist_to_ptv_centroids, dth (distance to target histogram), spread_x, spread_y, spread_z, cross_section_max, 
cross_section_median, columns added to DVHs
    * These columns can be added by clicking Create Tables from Settings view, if running from source
    * Running from Docker or pip install shouldn't need to do this manually
* dist_to_ptv_centroids and dth must be calculated from Admin view after proper ROI name mapping
* dth_string calculated with Calc PTV Dist in Admin view
    * the string stored is csv representing a histogram with 0.1mm bins
* centroid, spread, and cross-sections also calculated at time of import
    * calc in Admin view only required for data imported prior to 0.4.4 install
* Admin view now specifies Post-Import calculations via dropdown
    * Added choice "Default Post-Import" to run through all calcs not done at time of DICOM import
* Endpoints for review DVH now calculated

### 0.4.3 (2018.08.04)
* IMPORT_LATEST_ONLY removed from options.py in lieu of a simple checkbox in the admin view.
* Settings view now has functionality to edit parameters in options.py. These edits are stored 
in preferences/options via pickle.  If preferences/options does not exist, the default values in 
options.py are used.
* Draft of a user manual is now available.

### 0.4.2 (2018.07.31)
* Download button added for DVH endpoints.
* LITE_VIEW added to options.py. If this is set to True, only Query and DVHs tabs are rendered.  The 
DVHs tab is stripped down to only calculate endpoints, although they are not displayed.  This is 
to avoid any table or plots being  displayed. No correlation data is calculated.  Users working 
with VERY large datasets may find  this useful if all they want is to query and quickly calculate 
DVH endpoints.
* The download dropdown button on the Query tab has been non-functional since we updated for Bokeh 
0.13.0 compatibility.  This button works as expected now.

### 0.4.1 (2018.07.23)
* The DVH Analytics Docker image now has an empty file , /this_is_running_from_docker, 
which is used by DVH Analytics to detect if the user is running Docker. This helps 
DVH Analytics know where to look for SQL and import settings, as reflected in 
get_settings.py.
* The default behavior for adding a physician in the ROI Name Manager is to copy 
institutional ROIs as physician ROIs.
* The Admin view now has a feature to backup and restore preferences. This is mostly 
useful for backing up ROI maps. If you're using Docker, it's strongly recommended you backup your 
preferences since relaunching an image *may* restore your preference defaults.
* The database backup feature in the Admin view has been fixed to work with Docker. If you're running 
DVH Analytics source code locally, be sure you have the postgres sql command line tools installed, specifically 
pg_dumpall needs to be available.
* If a new physician was created in ROI Name Manager, and then ROI Map was saved while 
the newly added physician had no physician ROIs, an empty .roi file was created causing 
subsequent Admin view launches to crash.  This bug has been fixed; empty Physicians will not 
be stored and adding a new Physician automatically copies your institutional ROIs as 
physician ROIs.
* DVH Analytics is FINALLY using a change log.
