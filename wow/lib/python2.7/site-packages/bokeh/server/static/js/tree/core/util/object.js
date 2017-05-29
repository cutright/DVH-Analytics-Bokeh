"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.keys = Object.keys;
function values(object) {
    var keys = Object.keys(object);
    var length = keys.length;
    var values = new Array(length);
    for (var i = 0; i < length; i++) {
        values[i] = object[keys[i]];
    }
    return values;
}
exports.values = values;
function extend(dest) {
    var sources = [];
    for (var _i = 1; _i < arguments.length; _i++) {
        sources[_i - 1] = arguments[_i];
    }
    for (var _a = 0, sources_1 = sources; _a < sources_1.length; _a++) {
        var source = sources_1[_a];
        for (var key in source) {
            if (source.hasOwnProperty(key)) {
                dest[key] = source[key];
            }
        }
    }
    return dest;
}
exports.extend = extend;
function clone(obj) {
    return extend({}, obj);
}
exports.clone = clone;
function isEmpty(obj) {
    return Object.keys(obj).length === 0;
}
exports.isEmpty = isEmpty;
