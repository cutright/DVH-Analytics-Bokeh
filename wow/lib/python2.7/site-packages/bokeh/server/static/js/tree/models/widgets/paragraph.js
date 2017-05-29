"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var markup_1 = require("./markup");
var dom_1 = require("core/dom");
exports.ParagraphView = (function (superClass) {
    extend(ParagraphView, superClass);
    function ParagraphView() {
        return ParagraphView.__super__.constructor.apply(this, arguments);
    }
    ParagraphView.prototype.render = function () {
        var content;
        ParagraphView.__super__.render.call(this);
        content = dom_1.p({
            style: {
                margin: 0
            }
        }, this.model.text);
        return this.$el.find('.bk-markup').append(content);
    };
    return ParagraphView;
})(markup_1.MarkupView);
exports.Paragraph = (function (superClass) {
    extend(Paragraph, superClass);
    function Paragraph() {
        return Paragraph.__super__.constructor.apply(this, arguments);
    }
    Paragraph.prototype.type = "Paragraph";
    Paragraph.prototype.default_view = exports.ParagraphView;
    return Paragraph;
})(markup_1.Markup);
