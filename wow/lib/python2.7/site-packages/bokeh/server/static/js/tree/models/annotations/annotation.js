"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var side_panel_1 = require("core/layout/side_panel");
var p = require("core/properties");
var renderer_1 = require("../renderers/renderer");
exports.AnnotationView = (function (superClass) {
    extend(AnnotationView, superClass);
    function AnnotationView() {
        return AnnotationView.__super__.constructor.apply(this, arguments);
    }
    AnnotationView.prototype._get_panel_offset = function () {
        var x, y;
        x = this.model.panel._left._value;
        y = this.model.panel._bottom._value;
        return {
            x: x,
            y: -y
        };
    };
    AnnotationView.prototype._get_size = function () {
        return -1;
    };
    return AnnotationView;
})(renderer_1.RendererView);
exports.Annotation = (function (superClass) {
    extend(Annotation, superClass);
    function Annotation() {
        return Annotation.__super__.constructor.apply(this, arguments);
    }
    Annotation.prototype.type = 'Annotation';
    Annotation.prototype.default_view = exports.AnnotationView;
    Annotation.define({
        plot: [p.Instance]
    });
    Annotation.override({
        level: 'annotation'
    });
    Annotation.prototype.add_panel = function (side) {
        this.panel = new side_panel_1.SidePanel({
            side: side
        });
        this.panel.attach_document(this.document);
        return this.level = 'overlay';
    };
    return Annotation;
})(renderer_1.Renderer);
