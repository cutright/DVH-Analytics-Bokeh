"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var model_1 = require("../../model");
var p = require("core/properties");
exports.ToolEvents = (function (superClass) {
    extend(ToolEvents, superClass);
    function ToolEvents() {
        return ToolEvents.__super__.constructor.apply(this, arguments);
    }
    ToolEvents.prototype.type = 'ToolEvents';
    ToolEvents.define({
        geometries: [p.Array, []]
    });
    return ToolEvents;
})(model_1.Model);
