"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var solver_1 = require("./solver");
var model_1 = require("../../model");
var p = require("../properties");
exports.LayoutCanvas = (function (superClass) {
    extend(LayoutCanvas, superClass);
    function LayoutCanvas() {
        return LayoutCanvas.__super__.constructor.apply(this, arguments);
    }
    LayoutCanvas.prototype.type = 'LayoutCanvas';
    LayoutCanvas.prototype.initialize = function (attrs, options) {
        LayoutCanvas.__super__.initialize.call(this, attrs, options);
        this._top = new solver_1.Variable("top " + this.id);
        this._left = new solver_1.Variable("left " + this.id);
        this._width = new solver_1.Variable("width " + this.id);
        this._height = new solver_1.Variable("height " + this.id);
        this._right = new solver_1.Variable("right " + this.id);
        return this._bottom = new solver_1.Variable("bottom " + this.id);
    };
    LayoutCanvas.getters({
        height: function () {
            return this._height.value();
        },
        width: function () {
            return this._width.value();
        },
        right: function () {
            return this._right.value();
        },
        left: function () {
            return this._left.value();
        },
        top: function () {
            return this._top.value();
        },
        bottom: function () {
            return this._bottom.value();
        }
    });
    LayoutCanvas.internal({
        layout_location: [p.Any]
    });
    LayoutCanvas.prototype.get_edit_variables = function () {
        var editables;
        editables = [];
        editables.push({
            edit_variable: this._top,
            strength: solver_1.Strength.strong
        });
        editables.push({
            edit_variable: this._left,
            strength: solver_1.Strength.strong
        });
        editables.push({
            edit_variable: this._width,
            strength: solver_1.Strength.strong
        });
        editables.push({
            edit_variable: this._height,
            strength: solver_1.Strength.strong
        });
        return editables;
    };
    LayoutCanvas.prototype.get_constraints = function () {
        return [];
    };
    return LayoutCanvas;
})(model_1.Model);
