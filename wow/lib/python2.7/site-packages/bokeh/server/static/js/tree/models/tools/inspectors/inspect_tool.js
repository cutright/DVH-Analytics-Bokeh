"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var button_tool_1 = require("../button_tool");
exports.InspectToolView = (function (superClass) {
    extend(InspectToolView, superClass);
    function InspectToolView() {
        return InspectToolView.__super__.constructor.apply(this, arguments);
    }
    return InspectToolView;
})(button_tool_1.ButtonToolView);
exports.InspectTool = (function (superClass) {
    extend(InspectTool, superClass);
    function InspectTool() {
        return InspectTool.__super__.constructor.apply(this, arguments);
    }
    InspectTool.prototype.event_type = "move";
    InspectTool.override({
        active: true
    });
    return InspectTool;
})(button_tool_1.ButtonTool);
