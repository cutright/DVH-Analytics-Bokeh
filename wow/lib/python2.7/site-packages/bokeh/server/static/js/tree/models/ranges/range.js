"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var model_1 = require("../../model");
var p = require("core/properties");
exports.Range = (function (superClass) {
    extend(Range, superClass);
    function Range() {
        return Range.__super__.constructor.apply(this, arguments);
    }
    Range.prototype.type = 'Range';
    Range.prototype.initialize = function (options) {
        Range.__super__.initialize.call(this, options);
        return this.listenTo(this, 'change', function () {
            var ref;
            return (ref = this.callback) != null ? ref.execute(this) : void 0;
        });
    };
    Range.define({
        callback: [p.Instance]
    });
    Range.internal({
        plots: [p.Array, []]
    });
    Range.prototype.reset = function () {
        "This method should be reimplemented by subclasses and ensure that\nthe callback, if exists, is executed at completion.";
        return this.trigger('change');
    };
    return Range;
})(model_1.Model);
