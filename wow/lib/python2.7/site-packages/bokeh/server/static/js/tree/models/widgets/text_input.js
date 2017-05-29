"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var logging_1 = require("core/logging");
var p = require("core/properties");
var input_widget_1 = require("./input_widget");
var text_input_template_1 = require("./text_input_template");
exports.TextInputView = (function (superClass) {
    extend(TextInputView, superClass);
    function TextInputView() {
        return TextInputView.__super__.constructor.apply(this, arguments);
    }
    TextInputView.prototype.className = "bk-widget-form-group";
    TextInputView.prototype.template = text_input_template_1.default;
    TextInputView.prototype.events = {
        "change input": "change_input"
    };
    TextInputView.prototype.initialize = function (options) {
        TextInputView.__super__.initialize.call(this, options);
        this.render();
        return this.listenTo(this.model, 'change', this.render);
    };
    TextInputView.prototype.render = function () {
        TextInputView.__super__.render.call(this);
        this.$el.html(this.template(this.model.attributes));
        if (this.model.height) {
            this.$el.find('input').height(this.model.height - 35);
        }
        return this;
    };
    TextInputView.prototype.change_input = function () {
        var value;
        value = this.$el.find('input').val();
        logging_1.logger.debug("widget/text_input: value = " + value);
        this.model.value = value;
        return TextInputView.__super__.change_input.call(this);
    };
    return TextInputView;
})(input_widget_1.InputWidgetView);
exports.TextInput = (function (superClass) {
    extend(TextInput, superClass);
    function TextInput() {
        return TextInput.__super__.constructor.apply(this, arguments);
    }
    TextInput.prototype.type = "TextInput";
    TextInput.prototype.default_view = exports.TextInputView;
    TextInput.define({
        value: [p.String, ""],
        placeholder: [p.String, ""]
    });
    return TextInput;
})(input_widget_1.InputWidget);
