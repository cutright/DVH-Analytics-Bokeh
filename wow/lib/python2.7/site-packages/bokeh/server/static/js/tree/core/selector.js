"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var merge, extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var has_props_1 = require("./has_props");
var hittest = require("./hittest");
var p = require("./properties");
var array_1 = require("./util/array");
merge = function (obj1, obj2) {
    var arr1, arr2, i, key, keys, len, result;
    result = {};
    keys = array_1.concat(Object.keys(obj1), Object.keys(obj2));
    for (i = 0, len = keys.length; i < len; i++) {
        key = keys[i];
        arr1 = obj1[key] || [];
        arr2 = obj2[key] || [];
        result[key] = array_1.union(arr1, arr2);
    }
    return result;
};
exports.Selector = (function (superClass) {
    extend(Selector, superClass);
    function Selector() {
        return Selector.__super__.constructor.apply(this, arguments);
    }
    Selector.prototype.type = 'Selector';
    Selector.prototype.update = function (indices, final, append, silent) {
        if (silent == null) {
            silent = false;
        }
        this.setv('timestamp', new Date(), {
            silent: silent
        });
        this.setv('final', final, {
            silent: silent
        });
        if (append) {
            indices['0d'].indices = array_1.union(this.indices['0d'].indices, indices['0d'].indices);
            indices['0d'].glyph = this.indices['0d'].glyph || indices['0d'].glyph;
            indices['1d'].indices = array_1.union(this.indices['1d'].indices, indices['1d'].indices);
            indices['2d'].indices = merge(this.indices['2d'].indices, indices['2d'].indices);
        }
        return this.setv('indices', indices, {
            silent: silent
        });
    };
    Selector.prototype.clear = function () {
        this.timestamp = new Date();
        this.final = true;
        return this.indices = hittest.create_hit_test_result();
    };
    Selector.internal({
        indices: [
            p.Any, function () {
                return hittest.create_hit_test_result();
            }
        ],
        final: [p.Boolean],
        timestamp: [p.Any]
    });
    return Selector;
})(has_props_1.HasProps);
