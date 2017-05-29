"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var box_1 = require("./box");
exports.ColumnView = (function (superClass) {
    extend(ColumnView, superClass);
    function ColumnView() {
        return ColumnView.__super__.constructor.apply(this, arguments);
    }
    ColumnView.prototype.className = "bk-grid-column";
    return ColumnView;
})(box_1.BoxView);
exports.Column = (function (superClass) {
    extend(Column, superClass);
    Column.prototype.type = 'Column';
    Column.prototype.default_view = exports.ColumnView;
    function Column(attrs, options) {
        Column.__super__.constructor.call(this, attrs, options);
        this._horizontal = false;
    }
    return Column;
})(box_1.Box);
