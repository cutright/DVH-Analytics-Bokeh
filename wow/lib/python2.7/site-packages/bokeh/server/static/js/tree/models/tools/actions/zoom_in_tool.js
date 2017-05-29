"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var action_tool_1 = require("./action_tool");
var zoom_1 = require("core/util/zoom");
var p = require("core/properties");
exports.ZoomInToolView = (function (superClass) {
    extend(ZoomInToolView, superClass);
    function ZoomInToolView() {
        return ZoomInToolView.__super__.constructor.apply(this, arguments);
    }
    ZoomInToolView.prototype["do"] = function () {
        var dims, frame, h_axis, v_axis, zoom_info;
        frame = this.plot_model.frame;
        dims = this.model.dimensions;
        h_axis = dims === 'width' || dims === 'both';
        v_axis = dims === 'height' || dims === 'both';
        zoom_info = zoom_1.scale_range(frame, this.model.factor, h_axis, v_axis);
        this.plot_view.push_state('zoom_out', {
            range: zoom_info
        });
        this.plot_view.update_range(zoom_info, false, true);
        this.plot_view.interactive_timestamp = Date.now();
        return null;
    };
    return ZoomInToolView;
})(action_tool_1.ActionToolView);
exports.ZoomInTool = (function (superClass) {
    extend(ZoomInTool, superClass);
    function ZoomInTool() {
        return ZoomInTool.__super__.constructor.apply(this, arguments);
    }
    ZoomInTool.prototype.default_view = exports.ZoomInToolView;
    ZoomInTool.prototype.type = "ZoomInTool";
    ZoomInTool.prototype.tool_name = "Zoom In";
    ZoomInTool.prototype.icon = "bk-tool-icon-zoom-in";
    ZoomInTool.getters({
        tooltip: function () {
            return this._get_dim_tooltip(this.tool_name, this.dimensions);
        }
    });
    ZoomInTool.define({
        factor: [p.Percent, 0.1],
        dimensions: [p.Dimensions, "both"]
    });
    return ZoomInTool;
})(action_tool_1.ActionTool);
