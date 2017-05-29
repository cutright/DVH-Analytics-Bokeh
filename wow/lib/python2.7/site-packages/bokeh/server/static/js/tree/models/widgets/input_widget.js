"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var widget_1 = require("./widget");
var p = require("core/properties");
exports.InputWidgetView = (function (superClass) {
    extend(InputWidgetView, superClass);
    function InputWidgetView() {
        return InputWidgetView.__super__.constructor.apply(this, arguments);
    }
    InputWidgetView.prototype.render = function () {
        InputWidgetView.__super__.render.call(this);
        return this.$el.find('input').prop("disabled", this.model.disabled);
    };
    InputWidgetView.prototype.change_input = function () {
        var ref;
        return (ref = this.model.callback) != null ? ref.execute(this.model) : void 0;
    };
    return InputWidgetView;
})(widget_1.WidgetView);
exports.InputWidget = (function (superClass) {
    extend(InputWidget, superClass);
    function InputWidget() {
        return InputWidget.__super__.constructor.apply(this, arguments);
    }
    InputWidget.prototype.type = "InputWidget";
    InputWidget.prototype.default_view = exports.InputWidgetView;
    InputWidget.define({
        callback: [p.Instance],
        title: [p.String, '']
    });
    return InputWidget;
})(widget_1.Widget);
