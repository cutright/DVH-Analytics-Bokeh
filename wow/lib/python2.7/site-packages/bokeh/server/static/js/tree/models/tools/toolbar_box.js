"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty, indexOf = [].indexOf || function (item) { for (var i = 0, l = this.length; i < l; i++) {
    if (i in this && this[i] === item)
        return i;
} return -1; };
var p = require("core/properties");
var array_1 = require("core/util/array");
var action_tool_1 = require("./actions/action_tool");
var help_tool_1 = require("./actions/help_tool");
var gesture_tool_1 = require("./gestures/gesture_tool");
var inspect_tool_1 = require("./inspectors/inspect_tool");
var toolbar_base_1 = require("./toolbar_base");
var tool_proxy_1 = require("./tool_proxy");
var box_1 = require("../layouts/box");
exports.ToolbarBoxToolbar = (function (superClass) {
    extend(ToolbarBoxToolbar, superClass);
    function ToolbarBoxToolbar() {
        return ToolbarBoxToolbar.__super__.constructor.apply(this, arguments);
    }
    ToolbarBoxToolbar.prototype.type = 'ToolbarBoxToolbar';
    ToolbarBoxToolbar.prototype.default_view = toolbar_base_1.ToolbarBaseView;
    ToolbarBoxToolbar.prototype.initialize = function (options) {
        ToolbarBoxToolbar.__super__.initialize.call(this, options);
        this._init_tools();
        if (this.merge_tools === true) {
            return this._merge_tools();
        }
    };
    ToolbarBoxToolbar.define({
        merge_tools: [p.Bool, true]
    });
    ToolbarBoxToolbar.prototype._init_tools = function () {
        var et, i, len, ref, results, tool;
        ref = this.tools;
        results = [];
        for (i = 0, len = ref.length; i < len; i++) {
            tool = ref[i];
            if (tool instanceof inspect_tool_1.InspectTool) {
                if (!array_1.any(this.inspectors, (function (_this) {
                    return function (t) {
                        return t.id === tool.id;
                    };
                })(this))) {
                    results.push(this.inspectors = this.inspectors.concat([tool]));
                }
                else {
                    results.push(void 0);
                }
            }
            else if (tool instanceof help_tool_1.HelpTool) {
                if (!array_1.any(this.help, (function (_this) {
                    return function (t) {
                        return t.id === tool.id;
                    };
                })(this))) {
                    results.push(this.help = this.help.concat([tool]));
                }
                else {
                    results.push(void 0);
                }
            }
            else if (tool instanceof action_tool_1.ActionTool) {
                if (!array_1.any(this.actions, (function (_this) {
                    return function (t) {
                        return t.id === tool.id;
                    };
                })(this))) {
                    results.push(this.actions = this.actions.concat([tool]));
                }
                else {
                    results.push(void 0);
                }
            }
            else if (tool instanceof gesture_tool_1.GestureTool) {
                et = tool.event_type;
                if (!array_1.any(this.gestures[et].tools, (function (_this) {
                    return function (t) {
                        return t.id === tool.id;
                    };
                })(this))) {
                    results.push(this.gestures[et].tools = this.gestures[et].tools.concat([tool]));
                }
                else {
                    results.push(void 0);
                }
            }
            else {
                results.push(void 0);
            }
        }
        return results;
    };
    ToolbarBoxToolbar.prototype._merge_tools = function () {
        var actions, active, et, event_type, gestures, helptool, i, info, inspectors, j, k, l, len, len1, len2, len3, make_proxy, new_help_tools, new_help_urls, proxy, ref, ref1, ref2, ref3, ref4, ref5, ref6, results, tool, tool_type, tools;
        inspectors = {};
        actions = {};
        gestures = {};
        new_help_tools = [];
        new_help_urls = [];
        ref = this.help;
        for (i = 0, len = ref.length; i < len; i++) {
            helptool = ref[i];
            if (ref1 = helptool.redirect, indexOf.call(new_help_urls, ref1) < 0) {
                new_help_tools.push(helptool);
                new_help_urls.push(helptool.redirect);
            }
        }
        this.help = new_help_tools;
        ref2 = this.gestures;
        for (event_type in ref2) {
            info = ref2[event_type];
            if (!(event_type in gestures)) {
                gestures[event_type] = {};
            }
            ref3 = info.tools;
            for (j = 0, len1 = ref3.length; j < len1; j++) {
                tool = ref3[j];
                if (!(tool.type in gestures[event_type])) {
                    gestures[event_type][tool.type] = [];
                }
                gestures[event_type][tool.type].push(tool);
            }
        }
        ref4 = this.inspectors;
        for (k = 0, len2 = ref4.length; k < len2; k++) {
            tool = ref4[k];
            if (!(tool.type in inspectors)) {
                inspectors[tool.type] = [];
            }
            inspectors[tool.type].push(tool);
        }
        ref5 = this.actions;
        for (l = 0, len3 = ref5.length; l < len3; l++) {
            tool = ref5[l];
            if (!(tool.type in actions)) {
                actions[tool.type] = [];
            }
            actions[tool.type].push(tool);
        }
        make_proxy = function (tools, active) {
            if (active == null) {
                active = false;
            }
            return new tool_proxy_1.ToolProxy({
                tools: tools,
                event_type: tools[0].event_type,
                tooltip: tools[0].tool_name,
                tool_name: tools[0].tool_name,
                icon: tools[0].icon,
                active: active
            });
        };
        for (event_type in gestures) {
            this.gestures[event_type].tools = [];
            ref6 = gestures[event_type];
            for (tool_type in ref6) {
                tools = ref6[tool_type];
                if (tools.length > 0) {
                    proxy = make_proxy(tools);
                    this.gestures[event_type].tools.push(proxy);
                    this.listenTo(proxy, 'change:active', this._active_change.bind(proxy));
                }
            }
        }
        this.actions = [];
        for (tool_type in actions) {
            tools = actions[tool_type];
            if (tools.length > 0) {
                this.actions.push(make_proxy(tools));
            }
        }
        this.inspectors = [];
        for (tool_type in inspectors) {
            tools = inspectors[tool_type];
            if (tools.length > 0) {
                this.inspectors.push(make_proxy(tools, active = true));
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
            if (et !== 'pinch' && et !== 'scroll') {
                results.push(this.gestures[et].tools[0].active = true);
            }
            else {
                results.push(void 0);
            }
        }
        return results;
    };
    return ToolbarBoxToolbar;
})(toolbar_base_1.ToolbarBase);
exports.ToolbarBoxView = (function (superClass) {
    extend(ToolbarBoxView, superClass);
    function ToolbarBoxView() {
        return ToolbarBoxView.__super__.constructor.apply(this, arguments);
    }
    ToolbarBoxView.prototype.className = 'bk-toolbar-box';
    ToolbarBoxView.prototype.get_width = function () {
        if (this.model._horizontal === true) {
            return 30;
        }
        else {
            return null;
        }
    };
    ToolbarBoxView.prototype.get_height = function () {
        return 30;
    };
    return ToolbarBoxView;
})(box_1.BoxView);
exports.ToolbarBox = (function (superClass) {
    extend(ToolbarBox, superClass);
    function ToolbarBox() {
        return ToolbarBox.__super__.constructor.apply(this, arguments);
    }
    ToolbarBox.prototype.type = 'ToolbarBox';
    ToolbarBox.prototype.default_view = exports.ToolbarBoxView;
    ToolbarBox.prototype.initialize = function (options) {
        var ref;
        ToolbarBox.__super__.initialize.call(this, options);
        this._toolbar = new exports.ToolbarBoxToolbar(options);
        if ((ref = this.toolbar_location) === 'left' || ref === 'right') {
            this._horizontal = true;
            return this._toolbar._sizeable = this._toolbar._width;
        }
        else {
            this._horizontal = false;
            return this._toolbar._sizeable = this._toolbar._height;
        }
    };
    ToolbarBox.prototype._doc_attached = function () {
        return this._toolbar.attach_document(this.document);
    };
    ToolbarBox.prototype.get_layoutable_children = function () {
        return [this._toolbar];
    };
    ToolbarBox.define({
        toolbar_location: [p.Location, "right"],
        merge_tools: [p.Bool, true],
        tools: [p.Any, []],
        logo: [p.String, "normal"]
    });
    return ToolbarBox;
})(box_1.Box);
