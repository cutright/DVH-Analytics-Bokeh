"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var has_props_1 = require("../has_props");
var types_1 = require("./types");
exports.create_ref = function (obj) {
    var ref;
    if (!(obj instanceof has_props_1.HasProps)) {
        throw new Error("can only create refs for HasProps subclasses");
    }
    ref = {
        'type': obj.type,
        'id': obj.id
    };
    if (obj._subtype != null) {
        ref['subtype'] = obj._subtype;
    }
    return ref;
};
exports.is_ref = function (arg) {
    var keys;
    if (types_1.isObject(arg)) {
        keys = Object.keys(arg).sort();
        if (keys.length === 2) {
            return keys[0] === 'id' && keys[1] === 'type';
        }
        if (keys.length === 3) {
            return keys[0] === 'id' && keys[1] === 'subtype' && keys[2] === 'type';
        }
    }
    return false;
};
exports.convert_to_ref = function (value) {
    if (types_1.isArray(value)) {
        return value.map(exports.convert_to_ref);
    }
    else {
        if (value instanceof has_props_1.HasProps) {
            return value.ref();
        }
    }
};
