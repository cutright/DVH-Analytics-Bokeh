"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var _qbb, extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var spatial_1 = require("core/util/spatial");
var glyph_1 = require("./glyph");
_qbb = function (u, v, w) {
    var bd, t;
    if (v === (u + w) / 2) {
        return [u, w];
    }
    else {
        t = (u - v) / (u - 2 * v + w);
        bd = u * Math.pow(1 - t, 2) + 2 * v * (1 - t) * t + w * Math.pow(t, 2);
        return [Math.min(u, w, bd), Math.max(u, w, bd)];
    }
};
exports.QuadraticView = (function (superClass) {
    extend(QuadraticView, superClass);
    function QuadraticView() {
        return QuadraticView.__super__.constructor.apply(this, arguments);
    }
    QuadraticView.prototype._index_data = function () {
        var i, j, points, ref, ref1, ref2, x0, x1, y0, y1;
        points = [];
        for (i = j = 0, ref = this._x0.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
            if (isNaN(this._x0[i] + this._x1[i] + this._y0[i] + this._y1[i] + this._cx[i] + this._cy[i])) {
                continue;
            }
            ref1 = _qbb(this._x0[i], this._cx[i], this._x1[i]), x0 = ref1[0], x1 = ref1[1];
            ref2 = _qbb(this._y0[i], this._cy[i], this._y1[i]), y0 = ref2[0], y1 = ref2[1];
            points.push({
                minX: x0,
                minY: y0,
                maxX: x1,
                maxY: y1,
                i: i
            });
        }
        return new spatial_1.RBush(points);
    };
    QuadraticView.prototype._render = function (ctx, indices, arg) {
        var i, j, len, results, scx, scy, sx0, sx1, sy0, sy1;
        sx0 = arg.sx0, sy0 = arg.sy0, sx1 = arg.sx1, sy1 = arg.sy1, scx = arg.scx, scy = arg.scy;
        if (this.visuals.line.doit) {
            results = [];
            for (j = 0, len = indices.length; j < len; j++) {
                i = indices[j];
                if (isNaN(sx0[i] + sy0[i] + sx1[i] + sy1[i] + scx[i] + scy[i])) {
                    continue;
                }
                ctx.beginPath();
                ctx.moveTo(sx0[i], sy0[i]);
                ctx.quadraticCurveTo(scx[i], scy[i], sx1[i], sy1[i]);
                this.visuals.line.set_vectorize(ctx, i);
                results.push(ctx.stroke());
            }
            return results;
        }
    };
    QuadraticView.prototype.draw_legend_for_index = function (ctx, x0, x1, y0, y1, index) {
        return this._generic_line_legend(ctx, x0, x1, y0, y1, index);
    };
    return QuadraticView;
})(glyph_1.GlyphView);
exports.Quadratic = (function (superClass) {
    extend(Quadratic, superClass);
    function Quadratic() {
        return Quadratic.__super__.constructor.apply(this, arguments);
    }
    Quadratic.prototype.default_view = exports.QuadraticView;
    Quadratic.prototype.type = 'Quadratic';
    Quadratic.coords([['x0', 'y0'], ['x1', 'y1'], ['cx', 'cy']]);
    Quadratic.mixins(['line']);
    return Quadratic;
})(glyph_1.Glyph);
