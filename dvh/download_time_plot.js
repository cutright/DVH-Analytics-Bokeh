// Built from Bokeh Export CSV Example: 2017.04.27
// https://github.com/bokeh/bokeh/tree/master/examples/app/export_csv


var data = source_1.data;

var filetext = 'Group1\nmrn,x,y\n';
// Get data
for (i=0; i < data['mrn'].length; i++) {
    new_line = '';
    new_line = new_line.concat(data['mrn'][i]);
    new_line = new_line.concat(',');
    new_line = new_line.concat(data['date_str'][i]);
    new_line = new_line.concat(',');
    new_line = new_line.concat(data['y'][i]);
    new_line = new_line.concat('\n');
    filetext = filetext.concat(new_line);
}


var data = source_2.data;
filetext = filetext.concat('\n\n\nGroup2\nmrn,x,y\n');

// Get data
for (i=0; i < data['mrn'].length; i++) {
    new_line = '';
    new_line = new_line.concat(data['mrn'][i]);
    new_line = new_line.concat(',');
    new_line = new_line.concat(data['date_str'][i]);
    new_line = new_line.concat(',');
    new_line = new_line.concat(data['y'][i]);
    new_line = new_line.concat('\n');
    filetext = filetext.concat(new_line);
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