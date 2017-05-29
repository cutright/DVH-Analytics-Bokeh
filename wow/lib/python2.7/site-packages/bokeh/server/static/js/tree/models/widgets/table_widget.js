"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var widget_1 = require("./widget");
var p = require("core/properties");
exports.TableWidget = (function (superClass) {
    extend(TableWidget, superClass);
    function TableWidget() {
        return TableWidget.__super__.constructor.apply(this, arguments);
    }
    TableWidget.prototype.type = "TableWidget";
    TableWidget.define({
        source: [p.Instance]
    });
    return TableWidget;
})(widget_1.Widget);
