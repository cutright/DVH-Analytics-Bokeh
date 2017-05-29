"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty, slice = [].slice;
var tick_formatter_1 = require("./tick_formatter");
var p = require("core/properties");
var object_1 = require("core/util/object");
exports.FuncTickFormatter = (function (superClass) {
    extend(FuncTickFormatter, superClass);
    function FuncTickFormatter() {
        return FuncTickFormatter.__super__.constructor.apply(this, arguments);
    }
    FuncTickFormatter.prototype.type = 'FuncTickFormatter';
    FuncTickFormatter.define({
        args: [p.Any, {}],
        code: [p.String, '']
    });
    FuncTickFormatter.prototype.initialize = function (attrs, options) {
        return FuncTickFormatter.__super__.initialize.call(this, attrs, options);
    };
    FuncTickFormatter.prototype._make_func = function () {
        return (function (func, args, ctor) {
            ctor.prototype = func.prototype;
            var child = new ctor, result = func.apply(child, args);
            return Object(result) === result ? result : child;
        })(Function, ["tick"].concat(slice.call(Object.keys(this.args)), ["require"], [this.code]), function () { });
    };
    FuncTickFormatter.prototype.doFormat = function (ticks, loc) {
        var func, tick;
        func = this._make_func();
        return (function () {
            var i, len, results;
            results = [];
            for (i = 0, len = ticks.length; i < len; i++) {
                tick = ticks[i];
                results.push(func.apply(null, [tick].concat(slice.call(object_1.values(this.args)), [require])));
            }
            return results;
        }).call(this);
    };
    return FuncTickFormatter;
})(tick_formatter_1.TickFormatter);
