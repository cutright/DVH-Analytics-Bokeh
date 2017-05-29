//     Underscore.js 1.8.3
//     http://underscorejs.org
//     (c) 2009-2015 Jeremy Ashkenas, DocumentCloud and Investigative Reporters & Editors
//     Underscore may be freely distributed under the MIT license.
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var toString = Object.prototype.toString;
function isBoolean(obj) {
    return obj === true || obj === false || toString.call(obj) === '[object Boolean]';
}
exports.isBoolean = isBoolean;
function isNumber(obj) {
    return toString.call(obj) === "[object Number]";
}
exports.isNumber = isNumber;
function isString(obj) {
    return toString.call(obj) === "[object String]";
}
exports.isString = isString;
function isStrictNaN(obj) {
    return isNumber(obj) && obj !== +obj;
}
exports.isStrictNaN = isStrictNaN;
function isFunction(obj) {
    return toString.call(obj) === "[object Function]";
}
exports.isFunction = isFunction;
function isArray(obj) {
    return Array.isArray(obj);
}
exports.isArray = isArray;
function isObject(obj) {
    var tp = typeof obj;
    return tp === 'function' || tp === 'object' && !!obj;
}
exports.isObject = isObject;
