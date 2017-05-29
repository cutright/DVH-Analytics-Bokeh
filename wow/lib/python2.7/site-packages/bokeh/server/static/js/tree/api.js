"use strict";
function __export(m) {
    for (var p in m) if (!exports.hasOwnProperty(p)) exports[p] = m[p];
}
Object.defineProperty(exports, "__esModule", { value: true });
var object = require("./core/util/object");
var array = require("./core/util/array");
var string = require("./core/util/string");
var types = require("./core/util/types");
var eq = require("./core/util/eq");
exports.LinAlg = object.extend({}, object, array, string, types, eq);
var Charts = require("./api/charts");
exports.Charts = Charts;
var Plotting = require("./api/plotting");
exports.Plotting = Plotting;
var document_1 = require("./document");
exports.Document = document_1.Document;
var sprintf = require("sprintf");
exports.sprintf = sprintf;
__export(require("./api/models"));
