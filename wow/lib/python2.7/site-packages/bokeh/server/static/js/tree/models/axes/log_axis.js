"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var axis_1 = require("./axis");
var continuous_axis_1 = require("./continuous_axis");
var log_tick_formatter_1 = require("../formatters/log_tick_formatter");
var log_ticker_1 = require("../tickers/log_ticker");
exports.LogAxisView = (function (superClass) {
    extend(LogAxisView, superClass);
    function LogAxisView() {
        return LogAxisView.__super__.constructor.apply(this, arguments);
    }
    return LogAxisView;
})(axis_1.AxisView);
exports.LogAxis = (function (superClass) {
    extend(LogAxis, superClass);
    function LogAxis() {
        return LogAxis.__super__.constructor.apply(this, arguments);
    }
    LogAxis.prototype.default_view = exports.LogAxisView;
    LogAxis.prototype.type = 'LogAxis';
    LogAxis.override({
        ticker: function () {
            return new log_ticker_1.LogTicker();
        },
        formatter: function () {
            return new log_tick_formatter_1.LogTickFormatter();
        }
    });
    return LogAxis;
})(continuous_axis_1.ContinuousAxis);
