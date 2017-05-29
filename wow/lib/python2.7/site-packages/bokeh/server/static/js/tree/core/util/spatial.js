"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
/// <reference types="@types/rbush" />
var rbush = require("rbush");
var SpatialIndex = (function () {
    function SpatialIndex() {
    }
    return SpatialIndex;
}());
exports.SpatialIndex = SpatialIndex;
var RBush = (function (_super) {
    __extends(RBush, _super);
    function RBush(points) {
        var _this = _super.call(this) || this;
        _this.index = rbush();
        _this.index.load(points);
        return _this;
    }
    Object.defineProperty(RBush.prototype, "bbox", {
        get: function () {
            var _a = this.index.toJSON(), minX = _a.minX, minY = _a.minY, maxX = _a.maxX, maxY = _a.maxY;
            return { minX: minX, minY: minY, maxX: maxX, maxY: maxY };
        },
        enumerable: true,
        configurable: true
    });
    RBush.prototype.search = function (rect) {
        return this.index.search(rect);
    };
    RBush.prototype.indices = function (rect) {
        var points = this.search(rect);
        var n = points.length;
        var indices = new Array(n);
        for (var j = 0; j < n; j++) {
            indices[j] = points[j].i;
        }
        return indices;
    };
    return RBush;
}(SpatialIndex));
exports.RBush = RBush;
