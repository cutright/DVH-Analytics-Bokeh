"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var axis_1 = require("./axis");
exports.ContinuousAxis = (function (superClass) {
    extend(ContinuousAxis, superClass);
    function ContinuousAxis() {
        return ContinuousAxis.__super__.constructor.apply(this, arguments);
    }
    ContinuousAxis.prototype.type = 'ContinuousAxis';
    return ContinuousAxis;
})(axis_1.Axis);
