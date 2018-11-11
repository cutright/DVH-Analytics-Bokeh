// Built from Bokeh Export CSV Example: 2017.04.27
// https://github.com/bokeh/bokeh/tree/master/examples/app/export_csv


var data = source.data['text'][0]

if (cb_obj.value == 'anon_dvhs') {
    var data = source_anon.data['text'][0]}

if (cb_obj.value == 'lite') {
    var data = source_lite.data['text'][0]}

if (cb_obj.value == 'dvhs') {
    var data = source_dvhs.data['text'][0]}

var filename = 'data_result.csv';
var blob = new Blob([data], { type: 'text/csv;charset=utf-8;' });

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
