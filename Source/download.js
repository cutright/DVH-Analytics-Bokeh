var data = source.data;
var filetext = 'DVH Data\nmrn,uid,roi_name,roi_type,rx_dose,volume,min_dose,mean_dose,max_dose,eud,a\n';
for (i=0; i < data['mrn'].length; i++) {
    var currRow = [data['mrn'][i].toString(),
                   data['uid'][i].toString(),
                   data['roi_name'][i].toString(),
                   data['roi_type'][i].toString(),
                   data['rx_dose'][i].toString(),
                   data['volume'][i].toString(),
                   data['min_dose'][i].toString(),
                   data['mean_dose'][i].toString(),
                   data['max_dose'][i].toString(),
                   data['eud'][i].toString(),
                   data['eud_a_value'][i].toString().concat('\n')];

    var joined = currRow.join();
    filetext = filetext.concat(joined);
}

var data = source_rxs.data;
filetext = filetext.concat('\n\nRx Data\nmrn,uid,plan_name,fx_dose,rx_percent,rx_dose,fx_grp_count,fx_grp_name,');
filetext = filetext.concat('fx_grp_number,normalization_method,normalization_object\n');
for (i=0; i < data['mrn'].length; i++) {
    var currRow = [data['mrn'][i].toString(),
                   data['uid'][i].toString(),
                   data['plan_name'][i].toString(),
                   data['fx_dose'][i].toString(),
                   data['rx_percent'][i].toString(),
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
filetext = filetext.concat('\n\nPlan Data\nmrn,uid,age,birth_date,fxs,patient_orientation,patient_sex,physician,');
filetext = filetext.concat('rx_dose,sim_study_date,total_mu,tx_energies,tx_modality,tx_site\n');
for (i=0; i < data['mrn'].length; i++) {
    var currRow = [data['mrn'][i].toString(),
                   data['uid'][i].toString(),
                   data['age'][i].toString(),
                   data['birth_date'][i].toString(),
                   data['fxs'][i].toString(),
                   data['patient_orientation'][i].toString(),
                   data['patient_sex'][i].toString(),
                   data['physician'][i].toString(),
                   data['rx_dose'][i].toString(),
                   data['sim_study_date'][i].toString(),
                   data['total_mu'][i].toString(),
                   data['tx_energies'][i].toString(),
                   data['tx_modality'][i].toString(),
                   data['tx_site'][i].toString().concat('\n')];

    var joined = currRow.join();
    filetext = filetext.concat(joined);
}

var data = source_beams.data;
filetext = filetext.concat('\n\nBeam Data\nmrn,uid,beam_number,fx_count,fx_grp_beam_count,fx_grp_number,beam_name,beam_dose,');
filetext = filetext.concat('beam_energy,beam_mu,beam_type,collimator_angle,couch_angle,gantry_start,gantry_rot_dir,');
filetext = filetext.concat('gantry_end,radiation_type,ssd\n');
for (i=0; i < data['mrn'].length; i++) {
    var currRow = [data['mrn'][i].toString(),
                   data['uid'][i].toString(),
                   data['beam_number'][i].toString(),
                   data['fx_count'][i].toString(),
                   data['fx_grp_beam_count'][i].toString(),
                   data['fx_grp_number'][i].toString(),
                   data['beam_name'][i].toString(),
                   data['beam_dose'][i].toString(),
                   data['beam_energy'][i].toString(),
                   data['beam_mu'][i].toString(),
                   data['beam_type'][i].toString(),
                   data['collimator_angle'][i].toString(),
                   data['couch_angle'][i].toString(),
                   data['gantry_start'][i].toString(),
                   data['gantry_rot_dir'][i].toString(),
                   data['gantry_end'][i].toString(),
                   data['radiation_type'][i].toString(),
                   data['ssd'][i].toString().concat('\n')];

    var joined = currRow.join();
    filetext = filetext.concat(joined);
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