"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var bokeh_view_1 = require("core/bokeh_view");
var tool_1 = require("./tool");
var dom_1 = require("core/dom");
var p = require("core/properties");
exports.ButtonToolButtonView = (function (superClass) {
    extend(ButtonToolButtonView, superClass);
    function ButtonToolButtonView() {
        return ButtonToolButtonView.__super__.constructor.apply(this, arguments);
    }
    ButtonToolButtonView.prototype.className = "bk-toolbar-button";
    ButtonToolButtonView.prototype.initialize = function (options) {
        ButtonToolButtonView.__super__.initialize.call(this, options);
        this.listenTo(this.model, 'change', (function (_this) {
            return function () {
                return _this.render();
            };
        })(this));
        this.el.addEventListener("click", (function (_this) {
            return function (e) {
                return _this._clicked(e);
            };
        })(this));
        return this.render();
    };
    ButtonToolButtonView.prototype.render = function () {
        var icon, tip;
        dom_1.empty(this.el);
        this.el.disabled = this.model.disabled;
        icon = dom_1.div({
            "class": ['bk-btn-icon', this.model.icon]
        });
        tip = dom_1.span({
            "class": 'bk-tip'
        }, this.model.tooltip);
        this.el.appendChild(icon);
        return this.el.appendChild(tip);
    };
    ButtonToolButtonView.prototype._clicked = function (e) { };
    return ButtonToolButtonView;
})(bokeh_view_1.BokehView);
exports.ButtonToolView = (function (superClass) {
    extend(ButtonToolView, superClass);
    function ButtonToolView() {
        return ButtonToolView.__super__.constructor.apply(this, arguments);
    }
    return ButtonToolView;
})(tool_1.ToolView);
exports.ButtonTool = (function (superClass) {
    extend(ButtonTool, superClass);
    function ButtonTool() {
        return ButtonTool.__super__.constructor.apply(this, arguments);
    }
    ButtonTool.prototype.icon = null;
    ButtonTool.getters({
        tooltip: function () {
            return this.tool_name;
        }
    });
    ButtonTool.internal({
        disabled: [p.Boolean, false]
    });
    return ButtonTool;
})(tool_1.Tool);
