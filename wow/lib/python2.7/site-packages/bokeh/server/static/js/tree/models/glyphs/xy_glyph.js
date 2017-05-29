"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var spatial_1 = require("core/util/spatial");
var glyph_1 = require("./glyph");
var categorical_mapper_1 = require("../mappers/categorical_mapper");
exports.XYGlyphView = (function (superClass) {
    extend(XYGlyphView, superClass);
    function XYGlyphView() {
        return XYGlyphView.__super__.constructor.apply(this, arguments);
    }
    XYGlyphView.prototype._index_data = function () {
        var i, j, points, ref, x, xx, y, yy;
        if (this.renderer.xmapper instanceof categorical_mapper_1.CategoricalMapper) {
            xx = this.renderer.xmapper.v_map_to_target(this._x, true);
        }
        else {
            xx = this._x;
        }
        if (this.renderer.ymapper instanceof categorical_mapper_1.CategoricalMapper) {
            yy = this.renderer.ymapper.v_map_to_target(this._y, true);
        }
        else {
            yy = this._y;
        }
        points = [];
        for (i = j = 0, ref = xx.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
            x = xx[i];
            if (isNaN(x) || !isFinite(x)) {
                continue;
            }
            y = yy[i];
            if (isNaN(y) || !isFinite(y)) {
                continue;
            }
            points.push({
                minX: x,
                minY: y,
                maxX: x,
                maxY: y,
                i: i
            });
        }
        return new spatial_1.RBush(points);
    };
    return XYGlyphView;
})(glyph_1.GlyphView);
exports.XYGlyph = (function (superClass) {
    extend(XYGlyph, superClass);
    function XYGlyph() {
        return XYGlyph.__super__.constructor.apply(this, arguments);
    }
    XYGlyph.prototype.type = "XYGlyph";
    XYGlyph.prototype.default_view = exports.XYGlyphView;
    XYGlyph.coords([['x', 'y']]);
    return XYGlyph;
})(glyph_1.Glyph);
