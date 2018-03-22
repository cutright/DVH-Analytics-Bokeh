// Built from Bokeh Export CSV Example: 2017.04.27
// https://github.com/bokeh/bokeh/tree/master/examples/app/export_csv

var filetext = '';

var data = source_1_neg.data;

// Get columns
Object.keys(data).forEach(function(key,index) {
    // key: the name of the object key
    // index: the ordinal position of the key within the object
    filetext = filetext.concat(key);
    filetext = filetext.concat(',');
});
filetext = filetext.concat('\n');

// Get data
for (i=0; i < data['x'].length; i++) {
    new_line = '';
    Object.keys(data).forEach(function(key,index) {
        // key: the name of the object key
        // index: the ordinal position of the key within the object
        new_line = new_line.concat(data[key][i]);
        new_line = new_line.concat(',');
    });
    new_line = new_line.concat('\n');
    filetext = filetext.concat(new_line);
}

var data = source_1_pos.data;
// Get data
for (i=0; i < data['x'].length; i++) {
    new_line = '';
    Object.keys(data).forEach(function(key,index) {
        // key: the name of the object key
        // index: the ordinal position of the key within the object
        new_line = new_line.concat(data[key][i]);
        new_line = new_line.concat(',');
    });
    new_line = new_line.concat('\n');
    filetext = filetext.concat(new_line);
}

var data = source_2_neg.data;
// Get data
for (i=0; i < data['x'].length; i++) {
    new_line = '';
    Object.keys(data).forEach(function(key,index) {
        // key: the name of the object key
        // index: the ordinal position of the key within the object
        new_line = new_line.concat(data[key][i]);
        new_line = new_line.concat(',');
    });
    new_line = new_line.concat('\n');
    filetext = filetext.concat(new_line);
}

var data = source_2_pos.data;
// Get data
for (i=0; i < data['x'].length; i++) {
    new_line = '';
    Object.keys(data).forEach(function(key,index) {
        // key: the name of the object key
        // index: the ordinal position of the key within the object
        new_line = new_line.concat(data[key][i]);
        new_line = new_line.concat(',');
    });
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