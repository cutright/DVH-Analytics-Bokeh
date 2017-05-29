"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var widget_1 = require("./widget");
var p = require("core/properties");
exports.PanelView = (function (superClass) {
    extend(PanelView, superClass);
    function PanelView() {
        return PanelView.__super__.constructor.apply(this, arguments);
    }
    PanelView.prototype.render = function () {
        PanelView.__super__.render.call(this);
        this.$el.empty();
        return this;
    };
    return PanelView;
})(widget_1.WidgetView);
exports.Panel = (function (superClass) {
    extend(Panel, superClass);
    function Panel() {
        return Panel.__super__.constructor.apply(this, arguments);
    }
    Panel.prototype.type = "Panel";
    Panel.prototype.default_view = exports.PanelView;
    Panel.define({
        title: [p.String, ""],
        child: [p.Instance],
        closable: [p.Bool, false]
    });
    return Panel;
})(widget_1.Widget);
