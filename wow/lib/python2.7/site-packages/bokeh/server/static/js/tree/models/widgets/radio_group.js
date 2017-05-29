"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var $ = require("jquery");
var p = require("core/properties");
var string_1 = require("core/util/string");
var widget_1 = require("./widget");
exports.RadioGroupView = (function (superClass) {
    extend(RadioGroupView, superClass);
    function RadioGroupView() {
        return RadioGroupView.__super__.constructor.apply(this, arguments);
    }
    RadioGroupView.prototype.events = {
        "change input": "change_input"
    };
    RadioGroupView.prototype.initialize = function (options) {
        RadioGroupView.__super__.initialize.call(this, options);
        this.render();
        return this.listenTo(this.model, 'change', this.render);
    };
    RadioGroupView.prototype.render = function () {
        var $div, $input, $label, active, i, j, label, len, name, ref;
        RadioGroupView.__super__.render.call(this);
        this.$el.empty();
        name = string_1.uniqueId("RadioGroup");
        active = this.model.active;
        ref = this.model.labels;
        for (i = j = 0, len = ref.length; j < len; i = ++j) {
            label = ref[i];
            $input = $('<input type="radio">').attr({
                name: name,
                value: "" + i
            });
            if (this.model.disabled) {
                $input.prop("disabled", true);
            }
            if (i === active) {
                $input.prop("checked", true);
            }
            $label = $('<label></label>').text(label).prepend($input);
            if (this.model.inline) {
                $label.addClass("bk-bs-radio-inline");
                this.$el.append($label);
            }
            else {
                $div = $('<div class="bk-bs-radio"></div>').append($label);
                this.$el.append($div);
            }
        }
        return this;
    };
    RadioGroupView.prototype.change_input = function () {
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
    return RadioGroupView;
})(widget_1.WidgetView);
exports.RadioGroup = (function (superClass) {
    extend(RadioGroup, superClass);
    function RadioGroup() {
        return RadioGroup.__super__.constructor.apply(this, arguments);
    }
    RadioGroup.prototype.type = "RadioGroup";
    RadioGroup.prototype.default_view = exports.RadioGroupView;
    RadioGroup.define({
        active: [p.Any, null],
        labels: [p.Array, []],
        inline: [p.Bool, false],
        callback: [p.Instance]
    });
    return RadioGroup;
})(widget_1.Widget);
