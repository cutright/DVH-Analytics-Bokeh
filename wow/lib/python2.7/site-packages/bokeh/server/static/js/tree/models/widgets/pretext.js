"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var markup_1 = require("./markup");
var dom_1 = require("core/dom");
exports.PreTextView = (function (superClass) {
    extend(PreTextView, superClass);
    function PreTextView() {
        return PreTextView.__super__.constructor.apply(this, arguments);
    }
    PreTextView.prototype.render = function () {
        var content;
        PreTextView.__super__.render.call(this);
        content = dom_1.pre({
            style: {
                overflow: "auto"
            }
        }, this.model.text);
        return this.$el.find('.bk-markup').append(content);
    };
    return PreTextView;
})(markup_1.MarkupView);
exports.PreText = (function (superClass) {
    extend(PreText, superClass);
    function PreText() {
        return PreText.__super__.constructor.apply(this, arguments);
    }
    PreText.prototype.type = "PreText";
    PreText.prototype.default_view = exports.PreTextView;
    return PreText;
})(markup_1.Markup);
