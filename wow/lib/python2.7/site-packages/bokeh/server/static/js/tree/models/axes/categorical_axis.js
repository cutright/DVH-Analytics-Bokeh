"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var axis_1 = require("./axis");
var categorical_tick_formatter_1 = require("../formatters/categorical_tick_formatter");
var categorical_ticker_1 = require("../tickers/categorical_ticker");
var logging_1 = require("core/logging");
exports.CategoricalAxisView = (function (superClass) {
    extend(CategoricalAxisView, superClass);
    function CategoricalAxisView() {
        return CategoricalAxisView.__super__.constructor.apply(this, arguments);
    }
    return CategoricalAxisView;
})(axis_1.AxisView);
exports.CategoricalAxis = (function (superClass) {
    extend(CategoricalAxis, superClass);
    function CategoricalAxis() {
        return CategoricalAxis.__super__.constructor.apply(this, arguments);
    }
    CategoricalAxis.prototype.default_view = exports.CategoricalAxisView;
    CategoricalAxis.prototype.type = 'CategoricalAxis';
    CategoricalAxis.override({
        ticker: function () {
            return new categorical_ticker_1.CategoricalTicker();
        },
        formatter: function () {
            return new categorical_tick_formatter_1.CategoricalTickFormatter();
        }
    });
    CategoricalAxis.prototype._computed_bounds = function () {
        var cross_range, range, range_bounds, ref, ref1, user_bounds;
        ref = this.ranges, range = ref[0], cross_range = ref[1];
        user_bounds = (ref1 = this.bounds) != null ? ref1 : 'auto';
        range_bounds = [range.min, range.max];
        if (user_bounds !== 'auto') {
            logging_1.logger.warn("Categorical Axes only support user_bounds='auto', ignoring");
        }
        return range_bounds;
    };
    return CategoricalAxis;
})(axis_1.Axis);
