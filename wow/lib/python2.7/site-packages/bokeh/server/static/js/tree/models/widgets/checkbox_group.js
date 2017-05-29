"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty, indexOf = [].indexOf || function (item) { for (var i = 0, l = this.length; i < l; i++) {
    if (i in this && this[i] === item)
        return i;
} return -1; };
var $ = require("jquery");
var widget_1 = require("./widget");
var p = require("core/properties");
exports.CheckboxGroupView = (function (superClass) {
    extend(CheckboxGroupView, superClass);
    function CheckboxGroupView() {
        return CheckboxGroupView.__super__.constructor.apply(this, arguments);
    }
    CheckboxGroupView.prototype.events = {
        "change input": "change_input"
    };
    CheckboxGroupView.prototype.initialize = function (options) {
        CheckboxGroupView.__super__.initialize.call(this, options);
        this.render();
        return this.listenTo(this.model, 'change', this.render);
    };
    CheckboxGroupView.prototype.render = function () {
        var $div, $input, $label, active, i, j, label, len, ref;
        CheckboxGroupView.__super__.render.call(this);
        this.$el.empty();
        active = this.model.active;
        ref = this.model.labels;
        for (i = j = 0, len = ref.length; j < len; i = ++j) {
            label = ref[i];
            $input = $('<input type="checkbox">').attr({
                value: "" + i
            });
            if (this.model.disabled) {
                $input.prop("disabled", true);
            }
            if (indexOf.call(active, i) >= 0) {
                $input.prop("checked", true);
            }
            $label = $('<label></label>').text(label).prepend($input);
            if (this.model.inline) {
                $label.addClass("bk-bs-checkbox-inline");
                this.$el.append($label);
            }
            else {
                $div = $('<div class="bk-bs-checkbox"></div>').append($label);
                this.$el.append($div);
            }
        }
        return this;
    };
    CheckboxGroupView.prototype.change_input = function () {
        var active, checkbox, i, ref;
        active = (function () {
            var j, len, ref, results;
            ref = this.$el.find("input");
            results = [];
            for (i = j = 0, len = ref.length; j < len; i = ++j) {
                checkbox = ref[i];
                if (checkbox.checked) {
                    results.push(i);
                }
            }
            return results;
        }).call(this);
        this.model.active = active;
        return (ref = this.model.callback) != null ? ref.execute(this.model) : void 0;
    };
    return CheckboxGroupView;
})(widget_1.WidgetView);
exports.CheckboxGroup = (function (superClass) {
    extend(CheckboxGroup, superClass);
    function CheckboxGroup() {
        return CheckboxGroup.__super__.constructor.apply(this, arguments);
    }
    CheckboxGroup.prototype.type = "CheckboxGroup";
    CheckboxGroup.prototype.default_view = exports.CheckboxGroupView;
    CheckboxGroup.define({
        active: [p.Array, []],
        labels: [p.Array, []],
        inline: [p.Bool, false],
        callback: [p.Instance]
    });
    return CheckboxGroup;
})(widget_1.Widget);
