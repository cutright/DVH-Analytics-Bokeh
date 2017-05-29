"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var p = require("core/properties");
var build_views_1 = require("core/build_views");
var widget_1 = require("./widget");
var button_template_1 = require("./button_template");
exports.AbstractButtonView = (function (superClass) {
    extend(AbstractButtonView, superClass);
    function AbstractButtonView() {
        return AbstractButtonView.__super__.constructor.apply(this, arguments);
    }
    AbstractButtonView.prototype.events = {
        "click": "change_input"
    };
    AbstractButtonView.prototype.template = button_template_1.default;
    AbstractButtonView.prototype.initialize = function (options) {
        AbstractButtonView.__super__.initialize.call(this, options);
        this.icon_views = {};
        this.listenTo(this.model, 'change', this.render);
        return this.render();
    };
    AbstractButtonView.prototype.render = function () {
        var $button, html, icon, key, ref, ref1, val;
        AbstractButtonView.__super__.render.call(this);
        icon = this.model.icon;
        if (icon != null) {
            build_views_1.build_views(this.icon_views, [icon]);
            ref = this.icon_views;
            for (key in ref) {
                if (!hasProp.call(ref, key))
                    continue;
                val = ref[key];
                if ((ref1 = val.el.parentNode) != null) {
                    ref1.removeChild(val.el);
                }
            }
        }
        this.$el.empty();
        html = this.template(this.model.attributes);
        this.el.appendChild(html);
        $button = this.$el.find('button');
        if (icon != null) {
            $button.prepend("&nbsp;");
            $button.prepend(this.icon_views[icon.id].$el);
        }
        $button.prop("disabled", this.model.disabled);
        return this;
    };
    AbstractButtonView.prototype.change_input = function () {
        var ref;
        return (ref = this.model.callback) != null ? ref.execute(this.model) : void 0;
    };
    return AbstractButtonView;
})(widget_1.WidgetView);
exports.AbstractButton = (function (superClass) {
    extend(AbstractButton, superClass);
    function AbstractButton() {
        return AbstractButton.__super__.constructor.apply(this, arguments);
    }
    AbstractButton.prototype.type = "AbstractButton";
    AbstractButton.prototype.default_view = exports.AbstractButtonView;
    AbstractButton.define({
        callback: [p.Instance],
        label: [p.String, "Button"],
        icon: [p.Instance],
        button_type: [p.String, "default"]
    });
    return AbstractButton;
})(widget_1.Widget);
