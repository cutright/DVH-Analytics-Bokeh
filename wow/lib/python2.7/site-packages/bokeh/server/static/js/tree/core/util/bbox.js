"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
function empty() {
    return {
        minX: Infinity,
        minY: Infinity,
        maxX: -Infinity,
        maxY: -Infinity,
    };
}
exports.empty = empty;
function positive_x() {
    return {
        minX: Number.MIN_VALUE,
        minY: -Infinity,
        maxX: Infinity,
        maxY: Infinity,
    };
}
exports.positive_x = positive_x;
function positive_y() {
    return {
        minX: -Infinity,
        minY: Number.MIN_VALUE,
        maxX: Infinity,
        maxY: Infinity,
    };
}
exports.positive_y = positive_y;
function union(a, b) {
    return {
        minX: Math.min(a.minX, b.minX),
        maxX: Math.max(a.maxX, b.maxX),
        minY: Math.min(a.minY, b.minY),
        maxY: Math.max(a.maxY, b.maxY),
    };
}
exports.union = union;
var BBox = (function () {
    function BBox(bbox) {
        if (bbox == null) {
            this.x0 = Infinity;
            this.y0 = -Infinity;
            this.x1 = Infinity;
            this.y1 = -Infinity;
        }
        else {
            this.x0 = bbox.x0;
            this.y0 = bbox.y0;
            this.x1 = bbox.x1;
            this.y1 = bbox.y1;
        }
    }
    Object.defineProperty(BBox.prototype, "minX", {
        get: function () { return this.x0; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "minY", {
        get: function () { return this.y0; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "maxX", {
        get: function () { return this.x1; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "maxY", {
        get: function () { return this.y1; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "pt0", {
        get: function () { return [this.x0, this.y0]; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "pt1", {
        get: function () { return [this.x1, this.y1]; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "x", {
        get: function () { return this.x0; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "y", {
        get: function () { return this.x1; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "width", {
        get: function () { return this.x1 - this.x0; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(BBox.prototype, "height", {
        get: function () { return this.y1 - this.y0; },
        enumerable: true,
        configurable: true
    });
    BBox.prototype.contains = function (x, y) {
        return x >= this.x0 && x <= this.x1 && y >= this.y0 && y <= this.y1;
    };
    BBox.prototype.union = function (that) {
        return new BBox({
            x0: Math.min(this.x0, that.x0),
            y0: Math.min(this.y0, that.y0),
            x1: Math.max(this.x1, that.x1),
            y1: Math.max(this.y1, that.y1),
        });
    };
    return BBox;
}());
exports.BBox = BBox;
