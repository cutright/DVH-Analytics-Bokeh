"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend1 = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var logging_1 = require("core/logging");
var p = require("core/properties");
var object_1 = require("core/util/object");
var layout_dom_1 = require("../layouts/layout_dom");
exports.WidgetBoxView = (function (superClass) {
    extend1(WidgetBoxView, superClass);
    function WidgetBoxView() {
        return WidgetBoxView.__super__.constructor.apply(this, arguments);
    }
    WidgetBoxView.prototype.className = "bk-widget-box";
    WidgetBoxView.prototype.initialize = function (options) {
        WidgetBoxView.__super__.initialize.call(this, options);
        return this.render();
    };
    WidgetBoxView.prototype.bind_bokeh_events = function () {
        WidgetBoxView.__super__.bind_bokeh_events.call(this);
        return this.listenTo(this.model, 'change:children', (function (_this) {
            return function () {
                return _this.build_child_views();
            };
        })(this));
    };
    WidgetBoxView.prototype.render = function () {
        var css_width, height, s, width;
        s = this.model.document.solver();
        if (this.model.sizing_mode === 'fixed' || this.model.sizing_mode === 'scale_height') {
            width = this.get_width();
            if (this.model._width._value !== width) {
                s.suggest_value(this.model._width, width);
                s.update_variables();
            }
        }
        if (this.model.sizing_mode === 'fixed' || this.model.sizing_mode === 'scale_width') {
            height = this.get_height();
            if (this.model._height._value !== height) {
                s.suggest_value(this.model._height, height);
                s.update_variables();
            }
        }
        if (this.model._width._value - 20 > 0) {
            css_width = (this.model._width._value - 20) + "px";
        }
        else {
            css_width = "100%";
        }
        if (this.model.sizing_mode === 'stretch_both') {
            this.el.style.position = 'absolute';
            this.el.style.left = this.model._dom_left._value + "px";
            this.el.style.top = this.model._dom_top._value + "px";
            this.el.style.width = this.model._width._value + "px";
            return this.el.style.height = this.model._height._value + "px";
        }
        else {
            return this.el.style.width = css_width;
        }
    };
    WidgetBoxView.prototype.get_height = function () {
        var child_view, height, key, ref;
        height = 0;
        ref = this.child_views;
        for (key in ref) {
            if (!hasProp.call(ref, key))
                continue;
            child_view = ref[key];
            height += child_view.el.scrollHeight;
        }
        return height + 20;
    };
    WidgetBoxView.prototype.get_width = function () {
        var child_view, child_width, key, ref, width;
        if (this.model.width != null) {
            return this.model.width;
        }
        else {
            width = this.el.scrollWidth + 20;
            ref = this.child_views;
            for (key in ref) {
                if (!hasProp.call(ref, key))
                    continue;
                child_view = ref[key];
                child_width = child_view.el.scrollWidth;
                if (child_width > width) {
                    width = child_width;
                }
            }
            return width;
        }
    };
    return WidgetBoxView;
})(layout_dom_1.LayoutDOMView);
exports.WidgetBox = (function (superClass) {
    extend1(WidgetBox, superClass);
    function WidgetBox() {
        return WidgetBox.__super__.constructor.apply(this, arguments);
    }
    WidgetBox.prototype.type = 'WidgetBox';
    WidgetBox.prototype.default_view = exports.WidgetBoxView;
    WidgetBox.prototype.initialize = function (options) {
        WidgetBox.__super__.initialize.call(this, options);
        if (this.sizing_mode === 'fixed' && this.width === null) {
            this.width = 300;
            logging_1.logger.info("WidgetBox mode is fixed, but no width specified. Using default of 300.");
        }
        if (this.sizing_mode === 'scale_height') {
            return logging_1.logger.warn("sizing_mode `scale_height` is not experimental for WidgetBox. Please report your results to the bokeh dev team so we can improve.");
        }
    };
    WidgetBox.prototype.get_edit_variables = function () {
        var child, edit_variables, i, len, ref;
        edit_variables = WidgetBox.__super__.get_edit_variables.call(this);
        ref = this.get_layoutable_children();
        for (i = 0, len = ref.length; i < len; i++) {
            child = ref[i];
            edit_variables = edit_variables.concat(child.get_edit_variables());
        }
        return edit_variables;
    };
    WidgetBox.prototype.get_constraints = function () {
        var child, constraints, i, len, ref;
        constraints = WidgetBox.__super__.get_constraints.call(this);
        ref = this.get_layoutable_children();
        for (i = 0, len = ref.length; i < len; i++) {
            child = ref[i];
            constraints = constraints.concat(child.get_constraints());
        }
        return constraints;
    };
    WidgetBox.prototype.get_constrained_variables = function () {
        var constrained_variables;
        constrained_variables = WidgetBox.__super__.get_constrained_variables.call(this);
        constrained_variables = object_1.extend(constrained_variables, {
            'on-edge-align-top': this._top,
            'on-edge-align-bottom': this._height_minus_bottom,
            'on-edge-align-left': this._left,
            'on-edge-align-right': this._width_minus_right,
            'box-cell-align-top': this._top,
            'box-cell-align-bottom': this._height_minus_bottom,
            'box-cell-align-left': this._left,
            'box-cell-align-right': this._width_minus_right,
            'box-equal-size-top': this._top,
            'box-equal-size-bottom': this._height_minus_bottom
        });
        if (this.sizing_mode !== 'fixed') {
            constrained_variables = object_1.extend(constrained_variables, {
                'box-equal-size-left': this._left,
                'box-equal-size-right': this._width_minus_right
            });
        }
        return constrained_variables;
    };
    WidgetBox.prototype.get_layoutable_children = function () {
        return this.children;
    };
    WidgetBox.define({
        'children': [p.Array, []]
    });
    return WidgetBox;
})(layout_dom_1.LayoutDOM);
