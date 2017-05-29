"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var markup_1 = require("./markup");
var dom_1 = require("core/dom");
var p = require("core/properties");
exports.DivView = (function (superClass) {
    extend(DivView, superClass);
    function DivView() {
        return DivView.__super__.constructor.apply(this, arguments);
    }
    DivView.prototype.render = function () {
        var content;
        DivView.__super__.render.call(this);
        content = dom_1.div();
        if (this.model.render_as_text) {
            content.textContent = this.model.text;
        }
        else {
            content.innerHTML = this.model.text;
        }
        this.$el.find('.bk-markup').append(content);
        return this;
    };
    return DivView;
})(markup_1.MarkupView);
exports.Div = (function (superClass) {
    extend(Div, superClass);
    function Div() {
        return Div.__super__.constructor.apply(this, arguments);
    }
    Div.prototype.type = "Div";
    Div.prototype.default_view = exports.DivView;
    Div.define({
        render_as_text: [p.Bool, false]
    });
    return Div;
})(markup_1.Markup);
