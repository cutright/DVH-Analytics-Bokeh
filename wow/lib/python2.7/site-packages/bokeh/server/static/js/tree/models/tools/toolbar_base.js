"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty, bind = function (fn, me) { return function () { return fn.apply(me, arguments); }; };
var logging_1 = require("core/logging");
var solver_1 = require("core/layout/solver");
var dom_1 = require("core/dom");
var p = require("core/properties");
var layout_dom_1 = require("../layouts/layout_dom");
var action_tool_1 = require("./actions/action_tool");
var on_off_button_1 = require("./on_off_button");
var toolbar_template_1 = require("./toolbar_template");
exports.ToolbarBaseView = (function (superClass) {
    extend(ToolbarBaseView, superClass);
    function ToolbarBaseView() {
        return ToolbarBaseView.__super__.constructor.apply(this, arguments);
    }
    ToolbarBaseView.prototype.className = "bk-toolbar-wrapper";
    ToolbarBaseView.prototype.template = toolbar_template_1.default;
    ToolbarBaseView.prototype.render = function () {
        var buttons, et, gestures, i, j, k, l, len, len1, len2, len3, obj, ref, ref1, ref2, ref3;
        dom_1.empty(this.el);
        if (this.model.sizing_mode !== 'fixed') {
            this.el.style.left = this.model._dom_left._value + "px";
            this.el.style.top = this.model._dom_top._value + "px";
            this.el.style.width = this.model._width._value + "px";
            this.el.style.height = this.model._height._value + "px";
        }
        this.el.appendChild(this.template({
            logo: this.model.logo,
            location: this.model.toolbar_location,
            sticky: this.model.toolbar_sticky ? 'sticky' : 'not-sticky'
        }));
        buttons = this.el.querySelector(".bk-button-bar-list[type='inspectors']");
        ref = this.model.inspectors;
        for (i = 0, len = ref.length; i < len; i++) {
            obj = ref[i];
            buttons.appendChild(new on_off_button_1.OnOffButtonView({
                model: obj
            }).el);
        }
        buttons = this.el.querySelector(".bk-button-bar-list[type='help']");
        ref1 = this.model.help;
        for (j = 0, len1 = ref1.length; j < len1; j++) {
            obj = ref1[j];
            buttons.appendChild(new action_tool_1.ActionToolButtonView({
                model: obj
            }).el);
        }
        buttons = this.el.querySelector(".bk-button-bar-list[type='actions']");
        ref2 = this.model.actions;
        for (k = 0, len2 = ref2.length; k < len2; k++) {
            obj = ref2[k];
            buttons.appendChild(new action_tool_1.ActionToolButtonView({
                model: obj
            }).el);
        }
        gestures = this.model.gestures;
        for (et in gestures) {
            buttons = this.el.querySelector(".bk-button-bar-list[type='" + et + "']");
            ref3 = gestures[et].tools;
            for (l = 0, len3 = ref3.length; l < len3; l++) {
                obj = ref3[l];
                buttons.appendChild(new on_off_button_1.OnOffButtonView({
                    model: obj
                }).el);
            }
        }
        return this;
    };
    return ToolbarBaseView;
})(layout_dom_1.LayoutDOMView);
exports.ToolbarBase = (function (superClass) {
    extend(ToolbarBase, superClass);
    function ToolbarBase() {
        this._active_change = bind(this._active_change, this);
        return ToolbarBase.__super__.constructor.apply(this, arguments);
    }
    ToolbarBase.prototype.type = 'ToolbarBase';
    ToolbarBase.prototype.default_view = exports.ToolbarBaseView;
    ToolbarBase.prototype._active_change = function (tool) {
        var currently_active_tool, event_type, gestures;
        event_type = tool.event_type;
        gestures = this.gestures;
        currently_active_tool = gestures[event_type].active;
        if ((currently_active_tool != null) && currently_active_tool !== tool) {
            logging_1.logger.debug("Toolbar: deactivating tool: " + currently_active_tool.type + " (" + currently_active_tool.id + ") for event type '" + event_type + "'");
            currently_active_tool.active = false;
        }
        gestures[event_type].active = tool;
        this.gestures = gestures;
        logging_1.logger.debug("Toolbar: activating tool: " + tool.type + " (" + tool.id + ") for event type '" + event_type + "'");
        return null;
    };
    ToolbarBase.prototype.get_constraints = function () {
        var constraints;
        constraints = ToolbarBase.__super__.get_constraints.call(this);
        constraints.push(solver_1.EQ(this._sizeable, -30));
        return constraints;
    };
    ToolbarBase.define({
        tools: [p.Array, []],
        logo: [p.String, 'normal']
    });
    ToolbarBase.internal({
        gestures: [
            p.Any, function () {
                return {
                    pan: {
                        tools: [],
                        active: null
                    },
                    tap: {
                        tools: [],
                        active: null
                    },
                    doubletap: {
                        tools: [],
                        active: null
                    },
                    scroll: {
                        tools: [],
                        active: null
                    },
                    pinch: {
                        tools: [],
                        active: null
                    },
                    press: {
                        tools: [],
                        active: null
                    },
                    rotate: {
                        tools: [],
                        active: null
                    }
                };
            }
        ],
        actions: [p.Array, []],
        inspectors: [p.Array, []],
        help: [p.Array, []],
        toolbar_location: [p.Location, 'right'],
        toolbar_sticky: [p.Bool]
    });
    ToolbarBase.override({
        sizing_mode: null
    });
    return ToolbarBase;
})(layout_dom_1.LayoutDOM);
