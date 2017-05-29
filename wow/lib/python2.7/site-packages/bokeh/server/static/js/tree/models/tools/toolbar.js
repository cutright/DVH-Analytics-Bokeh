"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var p = require("core/properties");
var array_1 = require("core/util/array");
var action_tool_1 = require("./actions/action_tool");
var help_tool_1 = require("./actions/help_tool");
var gesture_tool_1 = require("./gestures/gesture_tool");
var inspect_tool_1 = require("./inspectors/inspect_tool");
var toolbar_base_1 = require("./toolbar_base");
exports.Toolbar = (function (superClass) {
    extend(Toolbar, superClass);
    function Toolbar() {
        return Toolbar.__super__.constructor.apply(this, arguments);
    }
    Toolbar.prototype.type = 'Toolbar';
    Toolbar.prototype.default_view = toolbar_base_1.ToolbarBaseView;
    Toolbar.prototype.initialize = function (attrs, options) {
        Toolbar.__super__.initialize.call(this, attrs, options);
        this.listenTo(this, 'change:tools', this._init_tools);
        return this._init_tools();
    };
    Toolbar.prototype._init_tools = function () {
        var et, i, len, ref, results, tool, tools;
        ref = this.tools;
        for (i = 0, len = ref.length; i < len; i++) {
            tool = ref[i];
            if (tool instanceof inspect_tool_1.InspectTool) {
                if (!array_1.any(this.inspectors, (function (_this) {
                    return function (t) {
                        return t.id === tool.id;
                    };
                })(this))) {
                    this.inspectors = this.inspectors.concat([tool]);
                }
            }
            else if (tool instanceof help_tool_1.HelpTool) {
                if (!array_1.any(this.help, (function (_this) {
                    return function (t) {
                        return t.id === tool.id;
                    };
                })(this))) {
                    this.help = this.help.concat([tool]);
                }
            }
            else if (tool instanceof action_tool_1.ActionTool) {
                if (!array_1.any(this.actions, (function (_this) {
                    return function (t) {
                        return t.id === tool.id;
                    };
                })(this))) {
                    this.actions = this.actions.concat([tool]);
                }
            }
            else if (tool instanceof gesture_tool_1.GestureTool) {
                et = tool.event_type;
                if (!(et in this.gestures)) {
                    logger.warn("Toolbar: unknown event type '" + et + "' for tool: " + tool.type + " (" + tool.id + ")");
                    continue;
                }
                if (!array_1.any(this.gestures[et].tools, (function (_this) {
                    return function (t) {
                        return t.id === tool.id;
                    };
                })(this))) {
                    this.gestures[et].tools = this.gestures[et].tools.concat([tool]);
                }
                this.listenTo(tool, 'change:active', this._active_change.bind(tool));
            }
        }
        results = [];
        for (et in this.gestures) {
            tools = this.gestures[et].tools;
            if (tools.length === 0) {
                continue;
            }
            this.gestures[et].tools = array_1.sortBy(tools, function (tool) {
                return tool.default_order;
            });
            if (et === 'tap') {
                if (this.active_tap === null) {
                    continue;
                }
                if (this.active_tap === 'auto') {
                    this.gestures[et].tools[0].active = true;
                }
                else {
                    this.active_tap.active = true;
                }
            }
            if (et === 'pan') {
                if (this.active_drag === null) {
                    continue;
                }
                if (this.active_drag === 'auto') {
                    this.gestures[et].tools[0].active = true;
                }
                else {
                    this.active_drag.active = true;
                }
            }
            if (et === 'pinch' || et === 'scroll') {
                if (this.active_scroll === null || this.active_scroll === 'auto') {
                    continue;
                }
                results.push(this.active_scroll.active = true);
            }
            else {
                results.push(void 0);
            }
        }
        return results;
    };
    Toolbar.define({
        active_drag: [p.Any, 'auto'],
        active_scroll: [p.Any, 'auto'],
        active_tap: [p.Any, 'auto']
    });
    return Toolbar;
})(toolbar_base_1.ToolbarBase);
