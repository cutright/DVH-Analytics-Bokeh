"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var spatial_1 = require("core/util/spatial");
var glyph_1 = require("./glyph");
var categorical_mapper_1 = require("../mappers/categorical_mapper");
var hittest = require("core/hittest");
var p = require("core/properties");
exports.VBarView = (function (superClass) {
    extend(VBarView, superClass);
    function VBarView() {
        return VBarView.__super__.constructor.apply(this, arguments);
    }
    VBarView.prototype._map_data = function () {
        var i, j, ref, vbottom, vtop;
        this.sx = this.renderer.xmapper.v_map_to_target(this._x);
        vtop = this.renderer.ymapper.v_map_to_target(this._top);
        vbottom = this.renderer.ymapper.v_map_to_target(this._bottom);
        this.stop = this.renderer.plot_view.canvas.v_vy_to_sy(vtop);
        this.sbottom = this.renderer.plot_view.canvas.v_vy_to_sy(vbottom);
        this.sleft = [];
        this.sright = [];
        this.sw = this.sdist(this.renderer.xmapper, this._x, this._width, 'center');
        for (i = j = 0, ref = this.sx.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
            this.sleft.push(this.sx[i] - this.sw[i] / 2);
            this.sright.push(this.sx[i] + this.sw[i] / 2);
        }
        return null;
    };
    VBarView.prototype._index_data = function () {
        var b, bottom, i, j, l, map_to_synthetic, points, r, ref, t, top, width, x;
        map_to_synthetic = function (mapper, array) {
            if (mapper instanceof categorical_mapper_1.CategoricalMapper) {
                return mapper.v_map_to_target(array, true);
            }
            else {
                return array;
            }
        };
        x = map_to_synthetic(this.renderer.xmapper, this._x);
        width = map_to_synthetic(this.renderer.xmapper, this._width);
        top = map_to_synthetic(this.renderer.ymapper, this._top);
        bottom = map_to_synthetic(this.renderer.ymapper, this._bottom);
        points = [];
        for (i = j = 0, ref = x.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
            l = x[i] - width[i] / 2;
            r = x[i] + width[i] / 2;
            t = top[i];
            b = bottom[i];
            if (isNaN(l + r + t + b) || !isFinite(l + r + t + b)) {
                continue;
            }
            points.push({
                minX: l,
                minY: b,
                maxX: r,
                maxY: t,
                i: i
            });
        }
        return new spatial_1.RBush(points);
    };
    VBarView.prototype._render = function (ctx, indices, arg) {
        var i, j, len, results, sbottom, sleft, sright, stop;
        sleft = arg.sleft, sright = arg.sright, stop = arg.stop, sbottom = arg.sbottom;
        results = [];
        for (j = 0, len = indices.length; j < len; j++) {
            i = indices[j];
            if (isNaN(sleft[i] + stop[i] + sright[i] + sbottom[i])) {
                continue;
            }
            if (this.visuals.fill.doit) {
                this.visuals.fill.set_vectorize(ctx, i);
                ctx.fillRect(sleft[i], stop[i], sright[i] - sleft[i], sbottom[i] - stop[i]);
            }
            if (this.visuals.line.doit) {
                ctx.beginPath();
                ctx.rect(sleft[i], stop[i], sright[i] - sleft[i], sbottom[i] - stop[i]);
                this.visuals.line.set_vectorize(ctx, i);
                results.push(ctx.stroke());
            }
            else {
                results.push(void 0);
            }
        }
        return results;
    };
    VBarView.prototype._hit_point = function (geometry) {
        var hits, ref, result, vx, vy, x, y;
        ref = [geometry.vx, geometry.vy], vx = ref[0], vy = ref[1];
        x = this.renderer.xmapper.map_from_target(vx, true);
        y = this.renderer.ymapper.map_from_target(vy, true);
        hits = this.index.indices({
            minX: x,
            minY: y,
            maxX: x,
            maxY: y
        });
        result = hittest.create_hit_test_result();
        result['1d'].indices = hits;
        return result;
    };
    VBarView.prototype.scy = function (i) {
        return (this.stop[i] + this.sbottom[i]) / 2;
    };
    VBarView.prototype.draw_legend_for_index = function (ctx, x0, x1, y0, y1, index) {
        return this._generic_area_legend(ctx, x0, x1, y0, y1, index);
    };
    return VBarView;
})(glyph_1.GlyphView);
exports.VBar = (function (superClass) {
    extend(VBar, superClass);
    function VBar() {
        return VBar.__super__.constructor.apply(this, arguments);
    }
    VBar.prototype.default_view = exports.VBarView;
    VBar.prototype.type = 'VBar';
    VBar.mixins(['line', 'fill']);
    VBar.define({
        x: [p.NumberSpec],
        width: [p.DistanceSpec],
        top: [p.NumberSpec],
        bottom: [p.NumberSpec, 0]
    });
    return VBar;
})(glyph_1.Glyph);
