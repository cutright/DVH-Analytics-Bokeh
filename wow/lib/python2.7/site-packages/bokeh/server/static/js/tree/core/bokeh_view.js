"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var Backbone = require("./backbone");
var string_1 = require("./util/string");
exports.BokehView = (function (superClass) {
    extend(BokehView, superClass);
    function BokehView() {
        return BokehView.__super__.constructor.apply(this, arguments);
    }
    BokehView.prototype.initialize = function (options) {
        if (options.id == null) {
            return this.id = string_1.uniqueId('BokehView');
        }
    };
    BokehView.prototype.toString = function () {
        return this.model.type + "View(" + this.id + ")";
    };
    BokehView.prototype.bind_bokeh_events = function () { };
    BokehView.prototype.remove = function () {
        this.trigger('remove', this);
        return BokehView.__super__.remove.call(this);
    };
    return BokehView;
})(Backbone.View);
