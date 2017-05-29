"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var adaptive_ticker_1 = require("./adaptive_ticker");
exports.BasicTicker = (function (superClass) {
    extend(BasicTicker, superClass);
    function BasicTicker() {
        return BasicTicker.__super__.constructor.apply(this, arguments);
    }
    BasicTicker.prototype.type = 'BasicTicker';
    return BasicTicker;
})(adaptive_ticker_1.AdaptiveTicker);
