"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var _format_number;
var SPrintf = require("sprintf");
var Numbro = require("numbro");
var string_1 = require("./string");
var types_1 = require("./types");
_format_number = function (number) {
    var format;
    if (types_1.isNumber(number)) {
        format = (function () {
            switch (false) {
                case Math.floor(number) !== number:
                    return "%d";
                case !(Math.abs(number) > 0.1 && Math.abs(number) < 1000):
                    return "%0.3f";
                default:
                    return "%0.3e";
            }
        })();
        return SPrintf.sprintf(format, number);
    }
    else {
        return "" + number;
    }
};
exports.replace_placeholders = function (string, data_source, i, special_vars) {
    if (special_vars == null) {
        special_vars = {};
    }
    string = string.replace(/(^|[^\$])\$(\w+)/g, (function (_this) {
        return function (match, prefix, name) {
            return prefix + "@$" + name;
        };
    })(this));
    string = string.replace(/(^|[^@])@(?:(\$?\w+)|{([^{}]+)})(?:{([^{}]+)})?/g, (function (_this) {
        return function (match, prefix, name, long_name, format) {
            var ref, replacement, value;
            name = long_name != null ? long_name : name;
            value = name[0] === "$" ? special_vars[name.substring(1)] : (ref = data_source.get_column(name)) != null ? ref[i] : void 0;
            replacement = null;
            if (value == null) {
                replacement = "???";
            }
            else {
                if (format === 'safe') {
                    return "" + prefix + value;
                }
                else if (format != null) {
                    replacement = Numbro.format(value, format);
                }
                else {
                    replacement = _format_number(value);
                }
            }
            return replacement = "" + prefix + (string_1.escape(replacement));
        };
    })(this));
    return string;
};
