"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var logging_1 = require("core/logging");
var p = require("core/properties");
var input_widget_1 = require("./input_widget");
var selecttemplate_1 = require("./selecttemplate");
exports.SelectView = (function (superClass) {
    extend(SelectView, superClass);
    function SelectView() {
        return SelectView.__super__.constructor.apply(this, arguments);
    }
    SelectView.prototype.template = selecttemplate_1.default;
    SelectView.prototype.events = {
        "change select": "change_input"
    };
    SelectView.prototype.initialize = function (options) {
        SelectView.__super__.initialize.call(this, options);
        this.render();
        return this.listenTo(this.model, 'change', this.render);
    };
    SelectView.prototype.render = function () {
        var html;
        SelectView.__super__.render.call(this);
        this.$el.empty();
        html = this.template(this.model.attributes);
        this.$el.html(html);
        return this;
    };
    SelectView.prototype.change_input = function () {
        var value;
        value = this.$el.find('select').val();
        logging_1.logger.debug("selectbox: value = " + value);
        this.model.value = value;
        return SelectView.__super__.change_input.call(this);
    };
    return SelectView;
})(input_widget_1.InputWidgetView);
exports.Select = (function (superClass) {
    extend(Select, superClass);
    function Select() {
        return Select.__super__.constructor.apply(this, arguments);
    }
    Select.prototype.type = "Select";
    Select.prototype.default_view = exports.SelectView;
    Select.define({
        value: [p.String, ''],
        options: [p.Any, []]
    });
    return Select;
})(input_widget_1.InputWidget);
