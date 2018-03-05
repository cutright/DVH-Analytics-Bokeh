// Built from Bokeh Export CSV Example: 2017.04.27
// https://github.com/bokeh/bokeh/tree/master/examples/app/export_csv

var filetext = '';

if (cb_obj.get('value') == 'anon_dvhs') {

    var data = source.data;
    var ep_names = source_endpoint_names.data;
    filetext = 'DVH Data\npatient#,roi_name,roi_type,rx_dose,volume,surface_area,min_dose,mean_dose,max_dose,dist_to_ptv_min,dist_to_ptv_mean,dist_to_ptv_median,dist_to_ptv_max,ptv_overlap\n';

    for (i=0; i < data['mrn'].length; i++) {
        var currRow = [data['anon_id'][i].toString(),
                       data['roi_name'][i].toString(),
                       data['roi_type'][i].toString(),
                       data['rx_dose'][i].toString(),
                       data['volume'][i].toString(),
                       data['surface_area'][i].toString(),
                       data['min_dose'][i].toString(),
                       data['mean_dose'][i].toString(),
                       data['max_dose'][i].toString(),
                       data['dist_to_ptv_min'][i].toString(),
                       data['dist_to_ptv_mean'][i].toString(),
                       data['dist_to_ptv_median'][i].toString(),
                       data['dist_to_ptv_max'][i].toString(),
                       data['ptv_overlap'][i].toString().concat('\n')];

        var joined = currRow.join();
        filetext = filetext.concat(joined);
    }

    var data = source_rxs.data;
    filetext = filetext.concat('\n\nRx Data\npatient#,plan_name,fx_dose,rx_percent,fxs,rx_dose,fx_grp_count,fx_grp_name,');
    filetext = filetext.concat('fx_grp_number,normalization_method,normalization_object\n');
    for (i=0; i < data['mrn'].length; i++) {
        var currRow = [data['anon_id'][i].toString(),
                       data['plan_name'][i].toString(),
                       data['fx_dose'][i].toString(),
                       data['rx_percent'][i].toString(),
                       data['fxs'][i].toString(),
                       data['rx_dose'][i].toString(),
                       data['fx_grp_count'][i].toString(),
                       data['fx_grp_name'][i].toString(),
                       data['fx_grp_number'][i].toString(),
                       data['normalization_method'][i].toString(),
                       data['normalization_object'][i].toString().concat('\n')];

        var joined = currRow.join();
        filetext = filetext.concat(joined);
    }

    var data = source.data;
    filetext = filetext.concat('\n\nDVHs\n');
    for (i=0; i < data['mrn'].length; i++) {
        filetext = filetext.concat(data['anon_id'][i]);
        filetext = filetext.concat(',,');
    }
    filetext = filetext.concat('\n');

    for (i=0; i < data['mrn'].length; i++) {
        filetext = filetext.concat(data['roi_name'][i]);
        filetext = filetext.concat(',,');
    }
    filetext = filetext.concat('\n');

    for (i=0; i < data['mrn'].length; i++) {
        filetext = filetext.concat('Dose (');
        filetext = filetext.concat(data['x_scale'][i]);
        filetext = filetext.concat('),');
        filetext = filetext.concat('Volume (');
        filetext = filetext.concat(data['y_scale'][i]);
        filetext = filetext.concat('),');
    }
    filetext = filetext.concat('\n');

    for (i=0; i < data['x'][1].length; i++) {
        for (j=0; j < data['mrn'].length; j++) {
            filetext = filetext.concat(data['x'][j][i]);
            filetext = filetext.concat(',');
            filetext = filetext.concat(data['y'][j][i]);
            filetext = filetext.concat(',');
            }
        filetext = filetext.concat('\n');
    }
}

if (cb_obj.get('value') == 'all' || cb_obj.get('value') == 'lite') {

    var data = source.data;
    filetext = 'DVH Data\nmrn,uid,roi_name,roi_type,rx_dose,volume,surface_area,min_dose,mean_dose,max_dose,dist_to_ptv_min,dist_to_ptv_mean,dist_to_ptv_median,dist_to_ptv_max,ptv_overlap\n';

    for (i=0; i < data['mrn'].length; i++) {
        var currRow = [data['mrn'][i].toString(),
                       data['uid'][i].toString(),
                       data['roi_name'][i].toString(),
                       data['roi_type'][i].toString(),
                       data['rx_dose'][i].toString(),
                       data['volume'][i].toString(),
                       data['surface_area'][i].toString(),
                       data['min_dose'][i].toString(),
                       data['mean_dose'][i].toString(),
                       data['max_dose'][i].toString(),
                       data['dist_to_ptv_min'][i].toString(),
                       data['dist_to_ptv_mean'][i].toString(),
                       data['dist_to_ptv_median'][i].toString(),
                       data['dist_to_ptv_max'][i].toString(),
                       data['ptv_overlap'][i].toString().concat('\n')];

        var joined = currRow.join();
        filetext = filetext.concat(joined);
    }

    var data = source_rxs.data;
    filetext = filetext.concat('\n\nRx Data\nmrn,uid,plan_name,fx_dose,rx_percent,fxs,rx_dose,fx_grp_count,fx_grp_name,');
    filetext = filetext.concat('fx_grp_number,normalization_method,normalization_object\n');
    for (i=0; i < data['mrn'].length; i++) {
        var currRow = [data['mrn'][i].toString(),
                       data['uid'][i].toString(),
                       data['plan_name'][i].toString(),
                       data['fx_dose'][i].toString(),
                       data['rx_percent'][i].toString(),
                       data['fxs'][i].toString(),
                       data['rx_dose'][i].toString(),
                       data['fx_grp_count'][i].toString(),
                       data['fx_grp_name'][i].toString(),
                       data['fx_grp_number'][i].toString(),
                       data['normalization_method'][i].toString(),
                       data['normalization_object'][i].toString().concat('\n')];

        var joined = currRow.join();
        filetext = filetext.concat(joined);
    }

    var data = source_plans.data;
    filetext = filetext.concat('\n\nPlan Data\nmrn,uid,age,birth_date,fxs,heterogeneity_correction,patient_orientation,');
    filetext = filetext.concat('patient_sex,physician,rx_dose,sim_study_date,total_mu,tx_modality,tx_site\n');
    for (i=0; i < data['mrn'].length; i++) {
        var currRow = [data['mrn'][i].toString(),
                       data['uid'][i].toString(),
                       data['age'][i].toString(),
                       data['birth_date'][i].toString(),
                       data['fxs'][i].toString(),
                       data['heterogeneity_correction'][i].toString(),
                       data['patient_orientation'][i].toString(),
                       data['patient_sex'][i].toString(),
                       data['physician'][i].toString(),
                       data['rx_dose'][i].toString(),
                       data['sim_study_date'][i].toString(),
                       data['total_mu'][i].toString(),
                       data['tx_modality'][i].toString(),
                       data['tx_site'][i].toString().concat('\n')];

        var joined = currRow.join();
        filetext = filetext.concat(joined);
    }
}

if (cb_obj.get('value') == 'all') {

    var data = source_beams.data;
    filetext = filetext.concat('\n\nBeam Data\nmrn,uid,beam_number,fxs,fx_grp_beam_count,fx_grp_number,');
    filetext = filetext.concat('beam_name,beam_dose,beam_energy_min,beam_energy_max,beam_mu,beam_type,scan_mode,');
    filetext = filetext.concat('scan_spot_count,control_point_count,radiation_type,ssd,treatment_machine,');
    filetext = filetext.concat('gantry_start,gantry_end,gantry_rot_dir,gantry_rot_dir,gantry_min,gantry_max,');
    filetext = filetext.concat('collimator_start,collimator_end,collimator_rot_dir,collimator_rot_dir,collimator_min,');
    filetext = filetext.concat('collimator_max,couch_start,couch_end,couch_rot_dir,couch_rot_dir,couch_min,couch_max\n');
    for (i=0; i < data['mrn'].length; i++) {
        var currRow = [data['mrn'][i].toString(),
                       data['uid'][i].toString(),
                       data['beam_number'][i].toString(),
                       data['fx_count'][i].toString(),
                       data['fx_grp_beam_count'][i].toString(),
                       data['fx_grp_number'][i].toString(),
                       data['beam_name'][i].toString(),
                       data['beam_dose'][i].toString(),
                       data['beam_energy_min'][i].toString(),
                       data['beam_energy_max'][i].toString(),
                       data['beam_mu'][i].toString(),
                       data['beam_type'][i].toString(),
                       data['scan_mode'][i].toString(),
                       data['scan_spot_count'][i].toString(),
                       data['control_point_count'][i].toString(),
                       data['radiation_type'][i].toString(),
                       data['ssd'][i].toString(),
                       data['treatment_machine'][i].toString(),
                       data['gantry_start'][i].toString(),
                       data['gantry_end'][i].toString(),
                       data['gantry_rot_dir'][i].toString(),
                       data['gantry_range'][i].toString(),
                       data['gantry_min'][i].toString(),
                       data['gantry_max'][i].toString(),
                       data['collimator_start'][i].toString(),
                       data['collimator_end'][i].toString(),
                       data['collimator_rot_dir'][i].toString(),
                       data['collimator_range'][i].toString(),
                       data['collimator_min'][i].toString(),
                       data['collimator_max'][i].toString(),
                       data['couch_start'][i].toString(),
                       data['couch_end'][i].toString(),
                       data['couch_rot_dir'][i].toString(),
                       data['couch_range'][i].toString(),
                       data['couch_min'][i].toString(),
                       data['couch_max'][i].toString().concat('\n')];

        var joined = currRow.join();
        filetext = filetext.concat(joined);
    }
}

if (cb_obj.get('value') == 'all' || cb_obj.get('value') == 'dvhs') {

    var data = source.data;
    filetext = filetext.concat('\n\nDVHs\n');
    for (i=0; i < data['mrn'].length; i++) {
        filetext = filetext.concat(data['mrn'][i]);
        filetext = filetext.concat(',,');
    }
    filetext = filetext.concat('\n');

    for (i=0; i < data['mrn'].length; i++) {
        filetext = filetext.concat(data['roi_name'][i]);
        filetext = filetext.concat(',,');
    }
    filetext = filetext.concat('\n');

    for (i=0; i < data['mrn'].length; i++) {
        filetext = filetext.concat('Dose (');
        filetext = filetext.concat(data['x_scale'][i]);
        filetext = filetext.concat('),');
        filetext = filetext.concat('Volume (');
        filetext = filetext.concat(data['y_scale'][i]);
        filetext = filetext.concat('),');
    }
    filetext = filetext.concat('\n');

    for (i=0; i < data['x'][1].length; i++) {
        for (j=0; j < data['mrn'].length; j++) {
            filetext = filetext.concat(data['x'][j][i]);
            filetext = filetext.concat(',');
            filetext = filetext.concat(data['y'][j][i]);
            filetext = filetext.concat(',');
            }
        filetext = filetext.concat('\n');
    }
}

var filename = 'data_result.csv';
var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename);
}

else {
    var link = document.createElement("a");
    link = document.createElement('a')
    link.href = URL.createObjectURL(blob);
    link.download = filename
    link.target = "_blank";
    link.style.visibility = 'hidden';
    link.dispatchEvent(new MouseEvent('click'))
}