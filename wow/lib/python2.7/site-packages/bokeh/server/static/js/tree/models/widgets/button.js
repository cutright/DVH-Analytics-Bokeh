"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var p = require("core/properties");
var bokeh_events_1 = require("core/bokeh_events");
var abstract_button_1 = require("./abstract_button");
exports.ButtonView = (function (superClass) {
    extend(ButtonView, superClass);
    function ButtonView() {
        return ButtonView.__super__.constructor.apply(this, arguments);
    }
    ButtonView.prototype.change_input = function () {
        this.model.trigger_event(new bokeh_events_1.ButtonClick({}));
        this.model.clicks = this.model.clicks + 1;
        return ButtonView.__super__.change_input.call(this);
    };
    return ButtonView;
})(abstract_button_1.AbstractButtonView);
exports.Button = (function (superClass) {
    extend(Button, superClass);
    function Button() {
        return Button.__super__.constructor.apply(this, arguments);
    }
    Button.prototype.type = "Button";
    Button.prototype.default_view = exports.ButtonView;
    Button.define({
        clicks: [p.Number, 0]
    });
    return Button;
})(abstract_button_1.AbstractButton);
bokeh_events_1.register_with_event(bokeh_events_1.ButtonClick, exports.Button);
