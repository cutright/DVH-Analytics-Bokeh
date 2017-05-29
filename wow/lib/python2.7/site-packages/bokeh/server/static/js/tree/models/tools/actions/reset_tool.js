"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var action_tool_1 = require("./action_tool");
var p = require("core/properties");
exports.ResetToolView = (function (superClass) {
    extend(ResetToolView, superClass);
    function ResetToolView() {
        return ResetToolView.__super__.constructor.apply(this, arguments);
    }
    ResetToolView.prototype["do"] = function () {
        this.plot_view.clear_state();
        this.plot_view.reset_range();
        this.plot_view.reset_selection();
        if (this.model.reset_size) {
            return this.plot_view.reset_dimensions();
        }
    };
    return ResetToolView;
})(action_tool_1.ActionToolView);
exports.ResetTool = (function (superClass) {
    extend(ResetTool, superClass);
    function ResetTool() {
        return ResetTool.__super__.constructor.apply(this, arguments);
    }
    ResetTool.prototype.default_view = exports.ResetToolView;
    ResetTool.prototype.type = "ResetTool";
    ResetTool.prototype.tool_name = "Reset";
    ResetTool.prototype.icon = "bk-tool-icon-reset";
    ResetTool.define({
        reset_size: [p.Bool, true]
    });
    return ResetTool;
})(action_tool_1.ActionTool);
