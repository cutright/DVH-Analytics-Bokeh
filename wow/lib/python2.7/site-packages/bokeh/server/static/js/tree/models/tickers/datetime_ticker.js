"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var ONE_HOUR, ONE_MILLI, ONE_MINUTE, ONE_MONTH, ONE_SECOND, extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var array_1 = require("core/util/array");
var adaptive_ticker_1 = require("./adaptive_ticker");
var composite_ticker_1 = require("./composite_ticker");
var days_ticker_1 = require("./days_ticker");
var months_ticker_1 = require("./months_ticker");
var years_ticker_1 = require("./years_ticker");
var util = require("./util");
ONE_MILLI = util.ONE_MILLI;
ONE_SECOND = util.ONE_SECOND;
ONE_MINUTE = util.ONE_MINUTE;
ONE_HOUR = util.ONE_HOUR;
ONE_MONTH = util.ONE_MONTH;
exports.DatetimeTicker = (function (superClass) {
    extend(DatetimeTicker, superClass);
    function DatetimeTicker() {
        return DatetimeTicker.__super__.constructor.apply(this, arguments);
    }
    DatetimeTicker.prototype.type = 'DatetimeTicker';
    DatetimeTicker.override({
        num_minor_ticks: 0,
        tickers: function () {
            return [
                new adaptive_ticker_1.AdaptiveTicker({
                    mantissas: [1, 2, 5],
                    base: 10,
                    min_interval: 0,
                    max_interval: 500 * ONE_MILLI,
                    num_minor_ticks: 0
                }), new adaptive_ticker_1.AdaptiveTicker({
                    mantissas: [1, 2, 5, 10, 15, 20, 30],
                    base: 60,
                    min_interval: ONE_SECOND,
                    max_interval: 30 * ONE_MINUTE,
                    num_minor_ticks: 0
                }), new adaptive_ticker_1.AdaptiveTicker({
                    mantissas: [1, 2, 4, 6, 8, 12],
                    base: 24.0,
                    min_interval: ONE_HOUR,
                    max_interval: 12 * ONE_HOUR,
                    num_minor_ticks: 0
                }), new days_ticker_1.DaysTicker({
                    days: array_1.range(1, 32)
                }), new days_ticker_1.DaysTicker({
                    days: array_1.range(1, 31, 3)
                }), new days_ticker_1.DaysTicker({
                    days: [1, 8, 15, 22]
                }), new days_ticker_1.DaysTicker({
                    days: [1, 15]
                }), new months_ticker_1.MonthsTicker({
                    months: array_1.range(0, 12, 1)
                }), new months_ticker_1.MonthsTicker({
                    months: array_1.range(0, 12, 2)
                }), new months_ticker_1.MonthsTicker({
                    months: array_1.range(0, 12, 4)
                }), new months_ticker_1.MonthsTicker({
                    months: array_1.range(0, 12, 6)
                }), new years_ticker_1.YearsTicker({})
            ];
        }
    });
    return DatetimeTicker;
})(composite_ticker_1.CompositeTicker);
