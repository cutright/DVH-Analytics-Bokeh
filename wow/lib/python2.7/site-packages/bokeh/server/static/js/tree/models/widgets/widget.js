"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var layout_dom_1 = require("../layouts/layout_dom");
var jqueryable_1 = require("./jqueryable");
exports.WidgetView = (function (superClass) {
    extend(WidgetView, superClass);
    function WidgetView() {
        return WidgetView.__super__.constructor.apply(this, arguments);
    }
    extend(WidgetView.prototype, jqueryable_1.JQueryable);
    WidgetView.prototype.className = "bk-widget";
    WidgetView.prototype.render = function () {
        if (this.model.height) {
            this.$el.height(this.model.height);
        }
        if (this.model.width) {
            return this.$el.width(this.model.width);
        }
    };
    return WidgetView;
})(layout_dom_1.LayoutDOMView);
exports.Widget = (function (superClass) {
    extend(Widget, superClass);
    function Widget() {
        return Widget.__super__.constructor.apply(this, arguments);
    }
    Widget.prototype.type = "Widget";
    Widget.prototype.default_view = exports.WidgetView;
    return Widget;
})(layout_dom_1.LayoutDOM);
