"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var linear_axis_1 = require("./linear_axis");
var datetime_tick_formatter_1 = require("../formatters/datetime_tick_formatter");
var datetime_ticker_1 = require("../tickers/datetime_ticker");
exports.DatetimeAxisView = (function (superClass) {
    extend(DatetimeAxisView, superClass);
    function DatetimeAxisView() {
        return DatetimeAxisView.__super__.constructor.apply(this, arguments);
    }
    return DatetimeAxisView;
})(linear_axis_1.LinearAxisView);
exports.DatetimeAxis = (function (superClass) {
    extend(DatetimeAxis, superClass);
    function DatetimeAxis() {
        return DatetimeAxis.__super__.constructor.apply(this, arguments);
    }
    DatetimeAxis.prototype.default_view = exports.DatetimeAxisView;
    DatetimeAxis.prototype.type = 'DatetimeAxis';
    DatetimeAxis.override({
        ticker: function () {
            return new datetime_ticker_1.DatetimeTicker();
        },
        formatter: function () {
            return new datetime_tick_formatter_1.DatetimeTickFormatter();
        }
    });
    return DatetimeAxis;
})(linear_axis_1.LinearAxis);
