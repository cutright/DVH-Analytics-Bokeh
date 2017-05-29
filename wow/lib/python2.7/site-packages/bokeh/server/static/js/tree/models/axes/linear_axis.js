"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var axis_1 = require("./axis");
var continuous_axis_1 = require("./continuous_axis");
var basic_tick_formatter_1 = require("../formatters/basic_tick_formatter");
var basic_ticker_1 = require("../tickers/basic_ticker");
exports.LinearAxisView = (function (superClass) {
    extend(LinearAxisView, superClass);
    function LinearAxisView() {
        return LinearAxisView.__super__.constructor.apply(this, arguments);
    }
    return LinearAxisView;
})(axis_1.AxisView);
exports.LinearAxis = (function (superClass) {
    extend(LinearAxis, superClass);
    function LinearAxis() {
        return LinearAxis.__super__.constructor.apply(this, arguments);
    }
    LinearAxis.prototype.default_view = exports.LinearAxisView;
    LinearAxis.prototype.type = 'LinearAxis';
    LinearAxis.override({
        ticker: function () {
            return new basic_ticker_1.BasicTicker();
        },
        formatter: function () {
            return new basic_tick_formatter_1.BasicTickFormatter();
        }
    });
    return LinearAxis;
})(continuous_axis_1.ContinuousAxis);
