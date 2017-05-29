"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var action_tool_1 = require("./action_tool");
exports.SaveToolView = (function (superClass) {
    extend(SaveToolView, superClass);
    function SaveToolView() {
        return SaveToolView.__super__.constructor.apply(this, arguments);
    }
    SaveToolView.prototype["do"] = function () {
        return this.plot_view.save("bokeh_plot.png");
    };
    return SaveToolView;
})(action_tool_1.ActionToolView);
exports.SaveTool = (function (superClass) {
    extend(SaveTool, superClass);
    function SaveTool() {
        return SaveTool.__super__.constructor.apply(this, arguments);
    }
    SaveTool.prototype.default_view = exports.SaveToolView;
    SaveTool.prototype.type = "SaveTool";
    SaveTool.prototype.tool_name = "Save";
    SaveTool.prototype.icon = "bk-tool-icon-save";
    return SaveTool;
})(action_tool_1.ActionTool);
