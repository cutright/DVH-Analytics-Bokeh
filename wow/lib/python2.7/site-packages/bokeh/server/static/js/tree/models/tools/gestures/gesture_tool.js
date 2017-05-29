"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var button_tool_1 = require("../button_tool");
exports.GestureToolView = (function (superClass) {
    extend(GestureToolView, superClass);
    function GestureToolView() {
        return GestureToolView.__super__.constructor.apply(this, arguments);
    }
    return GestureToolView;
})(button_tool_1.ButtonToolView);
exports.GestureTool = (function (superClass) {
    extend(GestureTool, superClass);
    function GestureTool() {
        return GestureTool.__super__.constructor.apply(this, arguments);
    }
    GestureTool.prototype.event_type = null;
    GestureTool.prototype.default_order = null;
    return GestureTool;
})(button_tool_1.ButtonTool);
