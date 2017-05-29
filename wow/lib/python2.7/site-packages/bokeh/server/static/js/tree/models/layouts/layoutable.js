"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var model_1 = require("../../model");
exports.LayoutableView = (function (superClass) {
    extend(LayoutableView, superClass);
    function LayoutableView() {
        return LayoutableView.__super__.constructor.apply(this, arguments);
    }
    return LayoutableView;
})(model_1.View);
exports.Layoutable = (function (superClass) {
    extend(Layoutable, superClass);
    function Layoutable() {
        return Layoutable.__super__.constructor.apply(this, arguments);
    }
    Layoutable.prototype.type = "Layoutable";
    return Layoutable;
})(model_1.Model);
