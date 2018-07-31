// Built from Bokeh Export CSV Example: 2017.04.27
// https://github.com/bokeh/bokeh/tree/master/examples/app/export_csv

var filetext = '';

var data = source.data;

// Get columns
filetext = "mrn,uid,group,roi_name,"
Object.keys(data).forEach(function(key,index) {
    // key: the name of the object key
    // index: the ordinal position of the key within the object
    if (key != 'mrn' && key != 'uid' && key != 'group' && key != 'roi_name'){
        filetext = filetext.concat(key);
        filetext = filetext.concat(',');
    }
});
filetext = filetext.concat('\n');

// Get data
for (i=0; i < data['mrn'].length; i++) {
    if (data['mrn'][i] != ''){
        new_line = '';
        new_line = new_line.concat(data['mrn'][i]);
        new_line = new_line.concat(',');
        new_line = new_line.concat(data['uid'][i]);
        new_line = new_line.concat(',');
        new_line = new_line.concat(data['group'][i]);
        new_line = new_line.concat(',');
        new_line = new_line.concat(data['roi_name'][i]);
        new_line = new_line.concat(',');

        Object.keys(data).forEach(function(key,index) {
            // key: the name of the object key
            // index: the ordinal position of the key within the object
            if (key != 'mrn' && key != 'uid' && key != 'group' && key != 'roi_name'){
                new_line = new_line.concat(data[key][i]);
                new_line = new_line.concat(',');
            }
        });
        new_line = new_line.concat('\n');
        filetext = filetext.concat(new_line);
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