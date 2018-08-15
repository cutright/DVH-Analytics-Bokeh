# Change log of DVH Analytics

### 0.4.4 (TBD)
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
* typo in keyword for parameter in dicom_to_sql (import_latest_plan_only changes to import_latest_only)

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