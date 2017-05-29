"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var widget_1 = require("./widget");
exports.AbstractIcon = (function (superClass) {
    extend(AbstractIcon, superClass);
    function AbstractIcon() {
        return AbstractIcon.__super__.constructor.apply(this, arguments);
    }
    AbstractIcon.prototype.type = "AbstractIcon";
    return AbstractIcon;
})(widget_1.Widget);
