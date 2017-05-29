"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend1 = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty, slice = [].slice;
var solver_1 = require("core/layout/solver");
var logging_1 = require("core/logging");
var p = require("core/properties");
var object_1 = require("core/util/object");
var types_1 = require("core/util/types");
var layout_dom_1 = require("../layouts/layout_dom");
var title_1 = require("../annotations/title");
var toolbar_1 = require("../tools/toolbar");
var tool_events_1 = require("../tools/tool_events");
var plot_canvas_1 = require("./plot_canvas");
var column_data_source_1 = require("../sources/column_data_source");
var glyph_renderer_1 = require("../renderers/glyph_renderer");
var bokeh_events_1 = require("core/bokeh_events");
exports.PlotView = (function (superClass) {
    extend1(PlotView, superClass);
    function PlotView() {
        return PlotView.__super__.constructor.apply(this, arguments);
    }
    PlotView.prototype.className = "bk-plot-layout";
    PlotView.prototype.bind_bokeh_events = function () {
        var title_msg;
        PlotView.__super__.bind_bokeh_events.call(this);
        title_msg = "Title object cannot be replaced. Try changing properties on title to update it after initialization.";
        return this.listenTo(this.model, 'change:title', (function (_this) {
            return function () {
                return logging_1.logger.warn(title_msg);
            };
        })(this));
    };
    PlotView.prototype.render = function () {
        var height, ref, s, width;
        PlotView.__super__.render.call(this);
        if (this.model.sizing_mode === 'scale_both') {
            ref = this.get_width_height(), width = ref[0], height = ref[1];
            s = this.model.document.solver();
            s.suggest_value(this.model._width, width);
            s.suggest_value(this.model._height, height);
            this.el.style.position = 'absolute';
            this.el.style.left = this.model._dom_left._value + "px";
            this.el.style.top = this.model._dom_top._value + "px";
            this.el.style.width = (this.model._width.value()) + "px";
            return this.el.style.height = (this.model._height.value()) + "px";
        }
    };
    PlotView.prototype.get_width_height = function () {
        var ar, height, new_height_1, new_height_2, new_width_1, new_width_2, parent_height, parent_width, width;
        parent_height = this.el.parentNode.clientHeight;
        parent_width = this.el.parentNode.clientWidth;
        ar = this.model.get_aspect_ratio();
        new_width_1 = parent_width;
        new_height_1 = parent_width / ar;
        new_width_2 = parent_height * ar;
        new_height_2 = parent_height;
        if (new_width_1 < new_width_2) {
            width = new_width_1;
            height = new_height_1;
        }
        else {
            width = new_width_2;
            height = new_height_2;
        }
        return [width, height];
    };
    PlotView.prototype.get_height = function () {
        return this.model._width._value / this.model.get_aspect_ratio();
    };
    PlotView.prototype.get_width = function () {
        return this.model._height._value * this.model.get_aspect_ratio();
    };
    PlotView.prototype.save = function (name) {
        var view;
        return ((function () {
            var i, len, ref, results;
            ref = object_1.values(this.child_views);
            results = [];
            for (i = 0, len = ref.length; i < len; i++) {
                view = ref[i];
                if (view instanceof plot_canvas_1.PlotCanvasView) {
                    results.push(view);
                }
            }
            return results;
        }).call(this))[0].save(name);
    };
    return PlotView;
})(layout_dom_1.LayoutDOMView);
exports.Plot = (function (superClass) {
    extend1(Plot, superClass);
    function Plot() {
        return Plot.__super__.constructor.apply(this, arguments);
    }
    Plot.prototype.type = 'Plot';
    Plot.prototype.default_view = exports.PlotView;
    Plot.prototype.initialize = function (options) {
        var i, j, len, len1, plots, ref, ref1, ref2, title, xr, yr;
        Plot.__super__.initialize.call(this, options);
        ref = object_1.values(this.extra_x_ranges).concat(this.x_range);
        for (i = 0, len = ref.length; i < len; i++) {
            xr = ref[i];
            plots = xr.plots;
            if (types_1.isArray(plots)) {
                plots = plots.concat(this);
                xr.setv('plots', plots, {
                    silent: true
                });
            }
        }
        ref1 = object_1.values(this.extra_y_ranges).concat(this.y_range);
        for (j = 0, len1 = ref1.length; j < len1; j++) {
            yr = ref1[j];
            plots = yr.plots;
            if (types_1.isArray(plots)) {
                plots = plots.concat(this);
                yr.setv('plots', plots, {
                    silent: true
                });
            }
        }
        this._horizontal = false;
        if ((ref2 = this.toolbar_location) === 'left' || ref2 === 'right') {
            this._horizontal = true;
        }
        if (this.min_border != null) {
            if (this.min_border_top == null) {
                this.min_border_top = this.min_border;
            }
            if (this.min_border_bottom == null) {
                this.min_border_bottom = this.min_border;
            }
            if (this.min_border_left == null) {
                this.min_border_left = this.min_border;
            }
            if (this.min_border_right == null) {
                this.min_border_right = this.min_border;
            }
        }
        if (this.title != null) {
            title = types_1.isString(this.title) ? new title_1.Title({
                text: this.title
            }) : this.title;
            this.add_layout(title, this.title_location);
        }
        this._plot_canvas = new plot_canvas_1.PlotCanvas({
            plot: this
        });
        this.toolbar.toolbar_location = this.toolbar_location;
        this.toolbar.toolbar_sticky = this.toolbar_sticky;
        this.plot_canvas.toolbar = this.toolbar;
        if (this.width == null) {
            this.width = this.plot_width;
        }
        if (this.height == null) {
            return this.height = this.plot_height;
        }
    };
    Plot.getter("plot_canvas", function () {
        return this._plot_canvas;
    });
    Plot.prototype._doc_attached = function () {
        var i, j, layout_renderers, len, len1, r, ref, side;
        ref = ['above', 'below', 'left', 'right'];
        for (i = 0, len = ref.length; i < len; i++) {
            side = ref[i];
            layout_renderers = this.getv(side);
            for (j = 0, len1 = layout_renderers.length; j < len1; j++) {
                r = layout_renderers[j];
                this.plot_canvas.add_renderer_to_canvas_side(r, side);
            }
        }
        this.plot_canvas.attach_document(this.document);
        this._set_orientation_variables(this);
        this._set_orientation_variables(this.toolbar);
        this._set_orientation_variables(this.plot_canvas);
        return Plot.__super__._doc_attached.call(this);
    };
    Plot.prototype.add_renderers = function () {
        var new_renderers, renderers;
        new_renderers = 1 <= arguments.length ? slice.call(arguments, 0) : [];
        renderers = this.renderers;
        renderers = renderers.concat(new_renderers);
        return this.renderers = renderers;
    };
    Plot.prototype.add_layout = function (renderer, side) {
        var side_renderers;
        if (side == null) {
            side = "center";
        }
        if (renderer.props.plot != null) {
            renderer.plot = this;
        }
        this.add_renderers(renderer);
        if (side !== 'center') {
            side_renderers = this.getv(side);
            return side_renderers.push(renderer);
        }
    };
    Plot.prototype.add_glyph = function (glyph, source, attrs) {
        var renderer;
        if (attrs == null) {
            attrs = {};
        }
        if (source == null) {
            source = new column_data_source_1.ColumnDataSource();
        }
        attrs = object_1.extend({}, attrs, {
            data_source: source,
            glyph: glyph
        });
        renderer = new glyph_renderer_1.GlyphRenderer(attrs);
        this.add_renderers(renderer);
        return renderer;
    };
    Plot.prototype.add_tools = function () {
        var attrs, new_tools, tool, tools;
        tools = 1 <= arguments.length ? slice.call(arguments, 0) : [];
        new_tools = (function () {
            var i, len, results;
            results = [];
            for (i = 0, len = tools.length; i < len; i++) {
                tool = tools[i];
                if (tool.overlay != null) {
                    this.add_renderers(tool.overlay);
                }
                if (tool.plot != null) {
                    results.push(tool);
                }
                else {
                    attrs = object_1.clone(tool.attributes);
                    attrs.plot = this;
                    results.push(new tool.constructor(attrs));
                }
            }
            return results;
        }).call(this);
        return this.toolbar.tools = this.toolbar.tools.concat(new_tools);
    };
    Plot.prototype.get_aspect_ratio = function () {
        return this.width / this.height;
    };
    Plot.prototype.get_layoutable_children = function () {
        var children;
        children = [this.plot_canvas];
        if (this.toolbar_location != null) {
            children = [this.toolbar, this.plot_canvas];
        }
        return children;
    };
    Plot.prototype.get_edit_variables = function () {
        var child, edit_variables, i, len, ref;
        edit_variables = Plot.__super__.get_edit_variables.call(this);
        if (this.sizing_mode === 'scale_both') {
            edit_variables.push({
                edit_variable: this._width,
                strength: solver_1.Strength.strong
            });
            edit_variables.push({
                edit_variable: this._height,
                strength: solver_1.Strength.strong
            });
        }
        ref = this.get_layoutable_children();
        for (i = 0, len = ref.length; i < len; i++) {
            child = ref[i];
            edit_variables = edit_variables.concat(child.get_edit_variables());
        }
        return edit_variables;
    };
    Plot.prototype.get_constraints = function () {
        var child, constraints, i, len, ref, ref1, ref2, sticky_edge;
        constraints = Plot.__super__.get_constraints.call(this);
        if (this.toolbar_location != null) {
            if (this.toolbar_sticky === true) {
                constraints.push(solver_1.EQ(this._sizeable, [-1, this.plot_canvas._sizeable]));
            }
            else {
                constraints.push(solver_1.EQ(this._sizeable, [-1, this.plot_canvas._sizeable], [-1, this.toolbar._sizeable]));
            }
            constraints.push(solver_1.EQ(this._full, [-1, this.plot_canvas._full]));
            if (this.toolbar_location === 'above') {
                sticky_edge = this.toolbar_sticky === true ? this.plot_canvas._top : this.plot_canvas._dom_top;
                constraints.push(solver_1.EQ(sticky_edge, [-1, this.toolbar._dom_top], [-1, this.toolbar._height]));
            }
            if (this.toolbar_location === 'below') {
                if (this.toolbar_sticky === false) {
                    constraints.push(solver_1.EQ(this.toolbar._dom_top, [-1, this.plot_canvas._height], this.toolbar._bottom, [-1, this.toolbar._height]));
                }
                if (this.toolbar_sticky === true) {
                    constraints.push(solver_1.GE(this.plot_canvas.below_panel._height, [-1, this.toolbar._height]));
                    constraints.push(solver_1.WEAK_EQ(this.toolbar._dom_top, [-1, this.plot_canvas._height], this.plot_canvas.below_panel._height));
                }
            }
            if (this.toolbar_location === 'left') {
                sticky_edge = this.toolbar_sticky === true ? this.plot_canvas._left : this.plot_canvas._dom_left;
                constraints.push(solver_1.EQ(sticky_edge, [-1, this.toolbar._dom_left], [-1, this.toolbar._width]));
            }
            if (this.toolbar_location === 'right') {
                if (this.toolbar_sticky === false) {
                    constraints.push(solver_1.EQ(this.toolbar._dom_left, [-1, this.plot_canvas._width], this.toolbar._right, [-1, this.toolbar._width]));
                }
                if (this.toolbar_sticky === true) {
                    constraints.push(solver_1.GE(this.plot_canvas.right_panel._width, [-1, this.toolbar._width]));
                    constraints.push(solver_1.WEAK_EQ(this.toolbar._dom_left, [-1, this.plot_canvas._width], this.plot_canvas.right_panel._width));
                }
            }
            if ((ref = this.toolbar_location) === 'above' || ref === 'below') {
                constraints.push(solver_1.EQ(this._width, [-1, this.toolbar._width], [-1, this.plot_canvas._width_minus_right]));
            }
            if ((ref1 = this.toolbar_location) === 'left' || ref1 === 'right') {
                constraints.push(solver_1.EQ(this._height, [-1, this.toolbar._height], [-1, this.plot_canvas.above_panel._height]));
                constraints.push(solver_1.EQ(this.toolbar._dom_top, [-1, this.plot_canvas.above_panel._height]));
            }
        }
        if (this.toolbar_location == null) {
            constraints.push(solver_1.EQ(this._width, [-1, this.plot_canvas._width]));
            constraints.push(solver_1.EQ(this._height, [-1, this.plot_canvas._height]));
        }
        ref2 = this.get_layoutable_children();
        for (i = 0, len = ref2.length; i < len; i++) {
            child = ref2[i];
            constraints = constraints.concat(child.get_constraints());
        }
        return constraints;
    };
    Plot.prototype.get_constrained_variables = function () {
        var constrained_variables;
        constrained_variables = Plot.__super__.get_constrained_variables.call(this);
        constrained_variables = object_1.extend(constrained_variables, {
            'on-edge-align-top': this.plot_canvas._top,
            'on-edge-align-bottom': this.plot_canvas._height_minus_bottom,
            'on-edge-align-left': this.plot_canvas._left,
            'on-edge-align-right': this.plot_canvas._width_minus_right,
            'box-cell-align-top': this.plot_canvas._top,
            'box-cell-align-bottom': this.plot_canvas._height_minus_bottom,
            'box-cell-align-left': this.plot_canvas._left,
            'box-cell-align-right': this.plot_canvas._width_minus_right,
            'box-equal-size-top': this.plot_canvas._top,
            'box-equal-size-bottom': this.plot_canvas._height_minus_bottom
        });
        if (this.sizing_mode !== 'fixed') {
            constrained_variables = object_1.extend(constrained_variables, {
                'box-equal-size-left': this.plot_canvas._left,
                'box-equal-size-right': this.plot_canvas._width_minus_right
            });
        }
        return constrained_variables;
    };
    Plot.prototype._set_orientation_variables = function (model) {
        if (this._horizontal === false) {
            model._sizeable = model._height;
            model._full = model._width;
        }
        if (this._horizontal === true) {
            model._sizeable = model._width;
            return model._full = model._height;
        }
    };
    Plot.mixins(['line:outline_', 'fill:background_', 'fill:border_']);
    Plot.define({
        toolbar: [
            p.Instance, function () {
                return new toolbar_1.Toolbar();
            }
        ],
        toolbar_location: [p.Location, 'right'],
        toolbar_sticky: [p.Bool, true],
        plot_width: [p.Number, 600],
        plot_height: [p.Number, 600],
        title: [
            p.Any, function () {
                return new title_1.Title({
                    text: ""
                });
            }
        ],
        title_location: [p.Location, 'above'],
        h_symmetry: [p.Bool, true],
        v_symmetry: [p.Bool, false],
        above: [p.Array, []],
        below: [p.Array, []],
        left: [p.Array, []],
        right: [p.Array, []],
        renderers: [p.Array, []],
        x_range: [p.Instance],
        extra_x_ranges: [p.Any, {}],
        y_range: [p.Instance],
        extra_y_ranges: [p.Any, {}],
        x_mapper_type: [p.String, 'auto'],
        y_mapper_type: [p.String, 'auto'],
        tool_events: [
            p.Instance, function () {
                return new tool_events_1.ToolEvents();
            }
        ],
        lod_factor: [p.Number, 10],
        lod_interval: [p.Number, 300],
        lod_threshold: [p.Number, 2000],
        lod_timeout: [p.Number, 500],
        webgl: [p.Bool, false],
        hidpi: [p.Bool, true],
        min_border: [p.Number, 5],
        min_border_top: [p.Number, null],
        min_border_left: [p.Number, null],
        min_border_bottom: [p.Number, null],
        min_border_right: [p.Number, null],
        inner_width: [p.Number],
        inner_height: [p.Number],
        layout_width: [p.Number],
        layout_height: [p.Number]
    });
    Plot.override({
        outline_line_color: '#e5e5e5',
        border_fill_color: "#ffffff",
        background_fill_color: "#ffffff"
    });
    Plot.getters({
        all_renderers: function () {
            var i, len, ref, renderers, tool;
            renderers = this.renderers;
            ref = this.toolbar.tools;
            for (i = 0, len = ref.length; i < len; i++) {
                tool = ref[i];
                renderers = renderers.concat(tool.synthetic_renderers);
            }
            return renderers;
        }
    });
    return Plot;
})(layout_dom_1.LayoutDOM);
bokeh_events_1.register_with_event(bokeh_events_1.UIEvent, exports.Plot);
