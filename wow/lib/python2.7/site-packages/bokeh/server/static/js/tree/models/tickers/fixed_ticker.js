"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var continuous_ticker_1 = require("./continuous_ticker");
var p = require("core/properties");
exports.FixedTicker = (function (superClass) {
    extend(FixedTicker, superClass);
    function FixedTicker() {
        return FixedTicker.__super__.constructor.apply(this, arguments);
    }
    FixedTicker.prototype.type = 'FixedTicker';
    FixedTicker.define({
        ticks: [p.Array, []]
    });
    FixedTicker.prototype.get_ticks_no_defaults = function (data_low, data_high, cross_loc, desired_n_ticks) {
        return {
            major: this.ticks,
            minor: []
        };
    };
    return FixedTicker;
})(continuous_ticker_1.ContinuousTicker);
