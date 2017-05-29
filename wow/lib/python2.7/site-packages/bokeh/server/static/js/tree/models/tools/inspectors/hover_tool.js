"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var _color_to_hex, extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var inspect_tool_1 = require("./inspect_tool");
var tooltip_1 = require("../../annotations/tooltip");
var glyph_renderer_1 = require("../../renderers/glyph_renderer");
var hittest = require("core/hittest");
var templating_1 = require("core/util/templating");
var dom_1 = require("core/dom");
var p = require("core/properties");
var object_1 = require("core/util/object");
var types_1 = require("core/util/types");
_color_to_hex = function (color) {
    var blue, digits, green, red, rgb;
    if (color.substr(0, 1) === '#') {
        return color;
    }
    digits = /(.*?)rgb\((\d+), (\d+), (\d+)\)/.exec(color);
    red = parseInt(digits[2]);
    green = parseInt(digits[3]);
    blue = parseInt(digits[4]);
    rgb = blue | (green << 8) | (red << 16);
    return digits[1] + '#' + rgb.toString(16);
};
exports.HoverToolView = (function (superClass) {
    extend(HoverToolView, superClass);
    function HoverToolView() {
        return HoverToolView.__super__.constructor.apply(this, arguments);
    }
    HoverToolView.prototype.bind_bokeh_events = function () {
        var k, len, r, ref;
        ref = this.model.computed_renderers;
        for (k = 0, len = ref.length; k < len; k++) {
            r = ref[k];
            this.listenTo(r.data_source, 'inspect', this._update);
        }
        return this.plot_view.canvas_view.el.style.cursor = "crosshair";
    };
    HoverToolView.prototype._clear = function () {
        var ref, results, rid, tt;
        this._inspect(2e308, 2e308);
        ref = this.model.ttmodels;
        results = [];
        for (rid in ref) {
            tt = ref[rid];
            results.push(tt.clear());
        }
        return results;
    };
    HoverToolView.prototype._move = function (e) {
        var canvas, vx, vy;
        if (!this.model.active) {
            return;
        }
        canvas = this.plot_view.canvas;
        vx = canvas.sx_to_vx(e.bokeh.sx);
        vy = canvas.sy_to_vy(e.bokeh.sy);
        if (!this.plot_view.frame.contains(vx, vy)) {
            return this._clear();
        }
        else {
            return this._inspect(vx, vy);
        }
    };
    HoverToolView.prototype._move_exit = function () {
        return this._clear();
    };
    HoverToolView.prototype._inspect = function (vx, vy, e) {
        var geometry, hovered_indexes, hovered_renderers, k, len, r, ref, sm;
        geometry = {
            type: 'point',
            vx: vx,
            vy: vy
        };
        if (this.model.mode === 'mouse') {
            geometry['type'] = 'point';
        }
        else {
            geometry['type'] = 'span';
            if (this.model.mode === 'vline') {
                geometry.direction = 'h';
            }
            else {
                geometry.direction = 'v';
            }
        }
        hovered_indexes = [];
        hovered_renderers = [];
        ref = this.model.computed_renderers;
        for (k = 0, len = ref.length; k < len; k++) {
            r = ref[k];
            sm = r.data_source.selection_manager;
            sm.inspect(this, this.plot_view.renderer_views[r.id], geometry, {
                "geometry": geometry
            });
        }
        if (this.model.callback != null) {
            this._emit_callback(geometry);
        }
    };
    HoverToolView.prototype._update = function (indices, tool, renderer, ds, arg) {
        var canvas, d1x, d1y, d2x, d2y, data_x, data_y, dist1, dist2, frame, geometry, i, j, k, l, len, len1, pt, ref, ref1, ref10, ref11, ref12, ref13, ref2, ref3, ref4, ref5, ref6, ref7, ref8, ref9, rx, ry, sdatax, sdatay, sx, sy, tooltip, vars, vx, vy, x, xmapper, y, ymapper;
        geometry = arg.geometry;
        tooltip = (ref = this.model.ttmodels[renderer.model.id]) != null ? ref : null;
        if (tooltip == null) {
            return;
        }
        tooltip.clear();
        if (indices['0d'].glyph === null && indices['1d'].indices.length === 0) {
            return;
        }
        vx = geometry.vx;
        vy = geometry.vy;
        canvas = this.plot_model.canvas;
        frame = this.plot_model.frame;
        sx = canvas.vx_to_sx(vx);
        sy = canvas.vy_to_sy(vy);
        xmapper = frame.x_mappers[renderer.model.x_range_name];
        ymapper = frame.y_mappers[renderer.model.y_range_name];
        x = xmapper.map_from_target(vx);
        y = ymapper.map_from_target(vy);
        ref1 = indices['0d'].indices;
        for (k = 0, len = ref1.length; k < len; k++) {
            i = ref1[k];
            data_x = renderer.glyph._x[i + 1];
            data_y = renderer.glyph._y[i + 1];
            switch (this.model.line_policy) {
                case "interp":
                    ref2 = renderer.glyph.get_interpolation_hit(i, geometry), data_x = ref2[0], data_y = ref2[1];
                    rx = xmapper.map_to_target(data_x);
                    ry = ymapper.map_to_target(data_y);
                    break;
                case "prev":
                    rx = canvas.sx_to_vx(renderer.glyph.sx[i]);
                    ry = canvas.sy_to_vy(renderer.glyph.sy[i]);
                    break;
                case "next":
                    rx = canvas.sx_to_vx(renderer.glyph.sx[i + 1]);
                    ry = canvas.sy_to_vy(renderer.glyph.sy[i + 1]);
                    break;
                case "nearest":
                    d1x = renderer.glyph.sx[i];
                    d1y = renderer.glyph.sy[i];
                    dist1 = hittest.dist_2_pts(d1x, d1y, sx, sy);
                    d2x = renderer.glyph.sx[i + 1];
                    d2y = renderer.glyph.sy[i + 1];
                    dist2 = hittest.dist_2_pts(d2x, d2y, sx, sy);
                    if (dist1 < dist2) {
                        ref3 = [d1x, d1y], sdatax = ref3[0], sdatay = ref3[1];
                    }
                    else {
                        ref4 = [d2x, d2y], sdatax = ref4[0], sdatay = ref4[1];
                        i = i + 1;
                    }
                    data_x = renderer.glyph._x[i];
                    data_y = renderer.glyph._y[i];
                    rx = canvas.sx_to_vx(sdatax);
                    ry = canvas.sy_to_vy(sdatay);
                    break;
                default:
                    ref5 = [vx, vy], rx = ref5[0], ry = ref5[1];
            }
            vars = {
                index: i,
                x: x,
                y: y,
                vx: vx,
                vy: vy,
                sx: sx,
                sy: sy,
                data_x: data_x,
                data_y: data_y,
                rx: rx,
                ry: ry
            };
            tooltip.add(rx, ry, this._render_tooltips(ds, i, vars));
        }
        ref6 = indices['1d'].indices;
        for (l = 0, len1 = ref6.length; l < len1; l++) {
            i = ref6[l];
            if (!object_1.isEmpty(indices['2d'].indices)) {
                ref7 = indices['2d'].indices;
                for (i in ref7) {
                    j = ref7[i][0];
                    data_x = renderer.glyph._xs[i][j];
                    data_y = renderer.glyph._ys[i][j];
                    switch (this.model.line_policy) {
                        case "interp":
                            ref8 = renderer.glyph.get_interpolation_hit(i, j, geometry), data_x = ref8[0], data_y = ref8[1];
                            rx = xmapper.map_to_target(data_x);
                            ry = ymapper.map_to_target(data_y);
                            break;
                        case "prev":
                            rx = canvas.sx_to_vx(renderer.glyph.sxs[i][j]);
                            ry = canvas.sy_to_vy(renderer.glyph.sys[i][j]);
                            break;
                        case "next":
                            rx = canvas.sx_to_vx(renderer.glyph.sxs[i][j + 1]);
                            ry = canvas.sy_to_vy(renderer.glyph.sys[i][j + 1]);
                            break;
                        case "nearest":
                            d1x = renderer.glyph.sx[i][j];
                            d1y = renderer.glyph.sy[i][j];
                            dist1 = hittest.dist_2_pts(d1x, d1y, sx, sy);
                            d2x = renderer.glyph.sx[i][j + 1];
                            d2y = renderer.glyph.sy[i][j + 1];
                            dist2 = hittest.dist_2_pts(d2x, d2y, sx, sy);
                            if (dist1 < dist2) {
                                ref9 = [d1x, d1y], sdatax = ref9[0], sdatay = ref9[1];
                            }
                            else {
                                ref10 = [d2x, d2y], sdatax = ref10[0], sdatay = ref10[1];
                                j = j + 1;
                            }
                            data_x = renderer.glyph._x[i][j];
                            data_y = renderer.glyph._y[i][j];
                            rx = canvas.sx_to_vx(sdatax);
                            ry = canvas.sy_to_vy(sdatay);
                    }
                    vars = {
                        index: i,
                        segment_index: j,
                        x: x,
                        y: y,
                        vx: vx,
                        vy: vy,
                        sx: sx,
                        sy: sy,
                        data_x: data_x,
                        data_y: data_y
                    };
                    tooltip.add(rx, ry, this._render_tooltips(ds, i, vars));
                }
            }
            else {
                data_x = (ref11 = renderer.glyph._x) != null ? ref11[i] : void 0;
                data_y = (ref12 = renderer.glyph._y) != null ? ref12[i] : void 0;
                if (this.model.point_policy === 'snap_to_data') {
                    pt = renderer.glyph.get_anchor_point(this.model.anchor, i, [sx, sy]);
                    if (pt == null) {
                        pt = renderer.glyph.get_anchor_point("center", i, [sx, sy]);
                    }
                    rx = canvas.sx_to_vx(pt.x);
                    ry = canvas.sy_to_vy(pt.y);
                }
                else {
                    ref13 = [vx, vy], rx = ref13[0], ry = ref13[1];
                }
                vars = {
                    index: i,
                    x: x,
                    y: y,
                    vx: vx,
                    vy: vy,
                    sx: sx,
                    sy: sy,
                    data_x: data_x,
                    data_y: data_y
                };
                tooltip.add(rx, ry, this._render_tooltips(ds, i, vars));
            }
        }
        return null;
    };
    HoverToolView.prototype._emit_callback = function (geometry) {
        var callback, canvas, data, frame, indices, obj, r, ref, xmapper, ymapper;
        r = this.model.computed_renderers[0];
        indices = this.plot_view.renderer_views[r.id].hit_test(geometry);
        canvas = this.plot_model.canvas;
        frame = this.plot_model.frame;
        geometry['sx'] = canvas.vx_to_sx(geometry.vx);
        geometry['sy'] = canvas.vy_to_sy(geometry.vy);
        xmapper = frame.x_mappers[r.x_range_name];
        ymapper = frame.y_mappers[r.y_range_name];
        geometry['x'] = xmapper.map_from_target(geometry.vx);
        geometry['y'] = ymapper.map_from_target(geometry.vy);
        callback = this.model.callback;
        ref = [
            callback, {
                index: indices,
                geometry: geometry
            }
        ], obj = ref[0], data = ref[1];
        if (types_1.isFunction(callback)) {
            callback(obj, data);
        }
        else {
            callback.execute(obj, data);
        }
    };
    HoverToolView.prototype._render_tooltips = function (ds, i, vars) {
        var cell, colname, color, column, el, hex, k, label, len, match, opts, ref, ref1, row, rows, swatch, tooltips, value;
        tooltips = this.model.tooltips;
        if (types_1.isString(tooltips)) {
            el = dom_1.div();
            el.innerHTML = templating_1.replace_placeholders(tooltips, ds, i, vars);
            return el;
        }
        else if (types_1.isFunction(tooltips)) {
            return tooltips(ds, vars);
        }
        else {
            rows = dom_1.div({
                style: {
                    display: "table",
                    borderSpacing: "2px"
                }
            });
            for (k = 0, len = tooltips.length; k < len; k++) {
                ref = tooltips[k], label = ref[0], value = ref[1];
                row = dom_1.div({
                    style: {
                        display: "table-row"
                    }
                });
                rows.appendChild(row);
                cell = dom_1.div({
                    style: {
                        display: "table-cell"
                    },
                    "class": 'bk-tooltip-row-label'
                }, label + ": ");
                row.appendChild(cell);
                cell = dom_1.div({
                    style: {
                        display: "table-cell"
                    },
                    "class": 'bk-tooltip-row-value'
                });
                row.appendChild(cell);
                if (value.indexOf("$color") >= 0) {
                    ref1 = value.match(/\$color(\[.*\])?:(\w*)/), match = ref1[0], opts = ref1[1], colname = ref1[2];
                    column = ds.get_column(colname);
                    if (column == null) {
                        el = dom_1.span({}, colname + " unknown");
                        cell.appendChild(el);
                        continue;
                    }
                    hex = (opts != null ? opts.indexOf("hex") : void 0) >= 0;
                    swatch = (opts != null ? opts.indexOf("swatch") : void 0) >= 0;
                    color = column[i];
                    if (color == null) {
                        el = dom_1.span({}, "(null)");
                        cell.appendChild(el);
                        continue;
                    }
                    if (hex) {
                        color = _color_to_hex(color);
                    }
                    el = dom_1.span({}, color);
                    cell.appendChild(el);
                    if (swatch) {
                        el = dom_1.span({
                            "class": 'bk-tooltip-color-block',
                            style: {
                                backgroundColor: color
                            }
                        }, " ");
                        cell.appendChild(el);
                    }
                }
                else {
                    value = value.replace("$~", "$data_");
                    el = dom_1.span();
                    el.innerHTML = templating_1.replace_placeholders(value, ds, i, vars);
                    cell.appendChild(el);
                }
            }
            return rows;
        }
    };
    return HoverToolView;
})(inspect_tool_1.InspectToolView);
exports.HoverTool = (function (superClass) {
    extend(HoverTool, superClass);
    function HoverTool() {
        return HoverTool.__super__.constructor.apply(this, arguments);
    }
    HoverTool.prototype.default_view = exports.HoverToolView;
    HoverTool.prototype.type = "HoverTool";
    HoverTool.prototype.tool_name = "Hover";
    HoverTool.prototype.icon = "bk-tool-icon-hover";
    HoverTool.define({
        tooltips: [p.Any, [["index", "$index"], ["data (x, y)", "($x, $y)"], ["canvas (x, y)", "($sx, $sy)"]]],
        renderers: [p.Array, []],
        names: [p.Array, []],
        mode: [p.String, 'mouse'],
        point_policy: [p.String, 'snap_to_data'],
        line_policy: [p.String, 'nearest'],
        show_arrow: [p.Boolean, true],
        anchor: [p.String, 'center'],
        attachment: [p.String, 'horizontal'],
        callback: [p.Any]
    });
    HoverTool.prototype.initialize = function (attrs, options) {
        HoverTool.__super__.initialize.call(this, attrs, options);
        this.define_computed_property('computed_renderers', function () {
            var all_renderers, names, r, renderers;
            renderers = this.renderers;
            names = this.names;
            if (renderers.length === 0) {
                all_renderers = this.plot.renderers;
                renderers = (function () {
                    var k, len, results;
                    results = [];
                    for (k = 0, len = all_renderers.length; k < len; k++) {
                        r = all_renderers[k];
                        if (r instanceof glyph_renderer_1.GlyphRenderer) {
                            results.push(r);
                        }
                    }
                    return results;
                })();
            }
            if (names.length > 0) {
                renderers = (function () {
                    var k, len, results;
                    results = [];
                    for (k = 0, len = renderers.length; k < len; k++) {
                        r = renderers[k];
                        if (names.indexOf(r.name) >= 0) {
                            results.push(r);
                        }
                    }
                    return results;
                })();
            }
            return renderers;
        }, true);
        this.add_dependencies('computed_renderers', this, ['renderers', 'names', 'plot']);
        this.add_dependencies('computed_renderers', this.plot, ['renderers']);
        this.define_computed_property('ttmodels', function () {
            var k, len, r, ref, tooltip, tooltips, ttmodels;
            ttmodels = {};
            tooltips = this.tooltips;
            if (tooltips != null) {
                ref = this.computed_renderers;
                for (k = 0, len = ref.length; k < len; k++) {
                    r = ref[k];
                    tooltip = new tooltip_1.Tooltip({
                        custom: types_1.isString(tooltips) || types_1.isFunction(tooltips),
                        attachment: this.attachment,
                        show_arrow: this.show_arrow
                    });
                    ttmodels[r.id] = tooltip;
                }
            }
            return ttmodels;
        });
        return this.add_dependencies('ttmodels', this, ['computed_renderers', 'tooltips']);
    };
    HoverTool.getters({
        computed_renderers: function () {
            return this._get_computed('computed_renderers');
        },
        ttmodels: function () {
            return this._get_computed('ttmodels');
        },
        synthetic_renderers: function () {
            return object_1.values(this.ttmodels);
        }
    });
    return HoverTool;
})(inspect_tool_1.InspectTool);
