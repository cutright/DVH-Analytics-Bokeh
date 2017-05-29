"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var range_1 = require("./range");
var p = require("core/properties");
exports.DataRange = (function (superClass) {
    extend(DataRange, superClass);
    function DataRange() {
        return DataRange.__super__.constructor.apply(this, arguments);
    }
    DataRange.prototype.type = 'DataRange';
    DataRange.define({
        names: [p.Array, []],
        renderers: [p.Array, []]
    });
    return DataRange;
})(range_1.Range);
