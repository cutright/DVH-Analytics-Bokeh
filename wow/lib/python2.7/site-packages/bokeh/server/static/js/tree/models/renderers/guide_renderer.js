"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var renderer_1 = require("./renderer");
var p = require("core/properties");
exports.GuideRenderer = (function (superClass) {
    extend(GuideRenderer, superClass);
    function GuideRenderer() {
        return GuideRenderer.__super__.constructor.apply(this, arguments);
    }
    GuideRenderer.prototype.type = 'GuideRenderer';
    GuideRenderer.define({
        plot: [p.Instance]
    });
    GuideRenderer.override({
        level: 'overlay'
    });
    return GuideRenderer;
})(renderer_1.Renderer);
