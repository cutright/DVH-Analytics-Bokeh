"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
require("bootstrap/button");
var dom_1 = require("core/dom");
var p = require("core/properties");
var string_1 = require("core/util/string");
var widget_1 = require("./widget");
var button_group_template_1 = require("./button_group_template");
exports.RadioButtonGroupView = (function (superClass) {
    extend(RadioButtonGroupView, superClass);
    function RadioButtonGroupView() {
        return RadioButtonGroupView.__super__.constructor.apply(this, arguments);
    }
    RadioButtonGroupView.prototype.events = {
        "change input": "change_input"
    };
    RadioButtonGroupView.prototype.template = button_group_template_1.default;
    RadioButtonGroupView.prototype.initialize = function (options) {
        RadioButtonGroupView.__super__.initialize.call(this, options);
        this.render();
        return this.listenTo(this.model, 'change', this.render);
    };
    RadioButtonGroupView.prototype.render = function () {
        var active, html, i, inputEl, j, labelEl, len, name, ref, text;
        RadioButtonGroupView.__super__.render.call(this);
        this.$el.empty();
        html = this.template();
        this.$el.append(html);
        name = string_1.uniqueId("RadioButtonGroup");
        active = this.model.active;
        ref = this.model.labels;
        for (i = j = 0, len = ref.length; j < len; i = ++j) {
            text = ref[i];
            inputEl = dom_1.input({
                type: "radio",
                name: name,
                value: "" + i,
                checked: i === active
            });
            labelEl = dom_1.label({
                "class": ["bk-bs-btn", "bk-bs-btn-" + this.model.button_type]
            }, inputEl, text);
            if (i === active) {
                labelEl.classList.add("bk-bs-active");
            }
            this.$el.find('.bk-bs-btn-group').append(labelEl);
        }
        return this;
    };
    RadioButtonGroupView.prototype.change_input = function () {
        var active, i, radio, ref;
        active = (function () {
            var j, len, ref, results;
            ref = this.$el.find("input");
            results = [];
            for (i = j = 0, len = ref.length; j < len; i = ++j) {
                radio = ref[i];
                if (radio.checked) {
                    results.push(i);
                }
            }
            return results;
        }).call(this);
        this.model.active = active[0];
        return (ref = this.model.callback) != null ? ref.execute(this.model) : void 0;
    };
    return RadioButtonGroupView;
})(widget_1.WidgetView);
exports.RadioButtonGroup = (function (superClass) {
    extend(RadioButtonGroup, superClass);
    function RadioButtonGroup() {
        return RadioButtonGroup.__super__.constructor.apply(this, arguments);
    }
    RadioButtonGroup.prototype.type = "RadioButtonGroup";
    RadioButtonGroup.prototype.default_view = exports.RadioButtonGroupView;
    RadioButtonGroup.define({
        active: [p.Any, null],
        labels: [p.Array, []],
        button_type: [p.String, "default"],
        callback: [p.Instance]
    });
    return RadioButtonGroup;
})(widget_1.Widget);
