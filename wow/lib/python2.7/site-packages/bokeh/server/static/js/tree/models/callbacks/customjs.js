"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty, slice = [].slice;
var p = require("core/properties");
var object_1 = require("core/util/object");
var model_1 = require("../../model");
exports.CustomJS = (function (superClass) {
    extend(CustomJS, superClass);
    function CustomJS() {
        return CustomJS.__super__.constructor.apply(this, arguments);
    }
    CustomJS.prototype.type = 'CustomJS';
    CustomJS.define({
        args: [p.Any, {}],
        code: [p.String, '']
    });
    CustomJS.getters({
        values: function () {
            return this._make_values();
        },
        func: function () {
            return this._make_func();
        }
    });
    CustomJS.prototype.execute = function (cb_obj, cb_data) {
        return this.func.apply(this, slice.call(this.values).concat([cb_obj], [cb_data], [require], [{}]));
    };
    CustomJS.prototype._make_values = function () {
        return object_1.values(this.args);
    };
    CustomJS.prototype._make_func = function () {
        return (function (func, args, ctor) {
            ctor.prototype = func.prototype;
            var child = new ctor, result = func.apply(child, args);
            return Object(result) === result ? result : child;
        })(Function, slice.call(Object.keys(this.args)).concat(["cb_obj"], ["cb_data"], ["require"], ["exports"], [this.code]), function () { });
    };
    return CustomJS;
})(model_1.Model);
