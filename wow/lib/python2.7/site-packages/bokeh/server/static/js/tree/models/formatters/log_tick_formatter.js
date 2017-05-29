"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var basic_tick_formatter_1 = require("./basic_tick_formatter");
var tick_formatter_1 = require("./tick_formatter");
var logging_1 = require("core/logging");
var p = require("core/properties");
exports.LogTickFormatter = (function (superClass) {
    extend(LogTickFormatter, superClass);
    function LogTickFormatter() {
        return LogTickFormatter.__super__.constructor.apply(this, arguments);
    }
    LogTickFormatter.prototype.type = 'LogTickFormatter';
    LogTickFormatter.define({
        ticker: [p.Instance, null]
    });
    LogTickFormatter.prototype.initialize = function (attrs, options) {
        LogTickFormatter.__super__.initialize.call(this, attrs, options);
        this.basic_formatter = new basic_tick_formatter_1.BasicTickFormatter();
        if (this.ticker == null) {
            return logging_1.logger.warn("LogTickFormatter not configured with a ticker, using default base of 10 (labels will be incorrect if ticker base is not 10)");
        }
    };
    LogTickFormatter.prototype.doFormat = function (ticks, loc) {
        var base, i, j, labels, ref, small_interval;
        if (ticks.length === 0) {
            return [];
        }
        if (this.ticker != null) {
            base = this.ticker.base;
        }
        else {
            base = 10;
        }
        small_interval = false;
        labels = new Array(ticks.length);
        for (i = j = 0, ref = ticks.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
            labels[i] = base + "^" + (Math.round(Math.log(ticks[i]) / Math.log(base)));
            if ((i > 0) && (labels[i] === labels[i - 1])) {
                small_interval = true;
                break;
            }
        }
        if (small_interval) {
            labels = this.basic_formatter.doFormat(ticks);
        }
        return labels;
    };
    return LogTickFormatter;
})(tick_formatter_1.TickFormatter);
