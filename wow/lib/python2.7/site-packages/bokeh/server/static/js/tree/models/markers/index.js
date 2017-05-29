"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var SQ3, _mk_model, _one_cross, _one_diamond, _one_tri, _one_x, asterisk, circle_cross, circle_x, cross, diamond, diamond_cross, inverted_triangle, square, square_cross, square_x, triangle, x, extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var marker_1 = require("./marker");
SQ3 = Math.sqrt(3);
_one_x = function (ctx, r) {
    ctx.moveTo(-r, r);
    ctx.lineTo(r, -r);
    ctx.moveTo(-r, -r);
    return ctx.lineTo(r, r);
};
_one_cross = function (ctx, r) {
    ctx.moveTo(0, r);
    ctx.lineTo(0, -r);
    ctx.moveTo(-r, 0);
    return ctx.lineTo(r, 0);
};
_one_diamond = function (ctx, r) {
    ctx.moveTo(0, r);
    ctx.lineTo(r / 1.5, 0);
    ctx.lineTo(0, -r);
    ctx.lineTo(-r / 1.5, 0);
    return ctx.closePath();
};
_one_tri = function (ctx, r) {
    var a, h;
    h = r * SQ3;
    a = h / 3;
    ctx.moveTo(-r, a);
    ctx.lineTo(r, a);
    ctx.lineTo(0, a - h);
    return ctx.closePath();
};
asterisk = function (ctx, i, sx, sy, r, line, fill) {
    var r2;
    r2 = r * 0.65;
    _one_cross(ctx, r);
    _one_x(ctx, r2);
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
};
circle_cross = function (ctx, i, sx, sy, r, line, fill) {
    ctx.arc(0, 0, r, 0, 2 * Math.PI, false);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        _one_cross(ctx, r);
        ctx.stroke();
    }
};
circle_x = function (ctx, i, sx, sy, r, line, fill) {
    ctx.arc(0, 0, r, 0, 2 * Math.PI, false);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        _one_x(ctx, r);
        ctx.stroke();
    }
};
cross = function (ctx, i, sx, sy, r, line, fill) {
    _one_cross(ctx, r);
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
};
diamond = function (ctx, i, sx, sy, r, line, fill) {
    _one_diamond(ctx, r);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
};
diamond_cross = function (ctx, i, sx, sy, r, line, fill) {
    _one_diamond(ctx, r);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        _one_cross(ctx, r);
        ctx.stroke();
    }
};
inverted_triangle = function (ctx, i, sx, sy, r, line, fill) {
    ctx.rotate(Math.PI);
    _one_tri(ctx, r);
    ctx.rotate(-Math.PI);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
};
square = function (ctx, i, sx, sy, r, line, fill) {
    var size;
    size = 2 * r;
    ctx.rect(-r, -r, size, size);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
};
square_cross = function (ctx, i, sx, sy, r, line, fill) {
    var size;
    size = 2 * r;
    ctx.rect(-r, -r, size, size);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        _one_cross(ctx, r);
        ctx.stroke();
    }
};
square_x = function (ctx, i, sx, sy, r, line, fill) {
    var size;
    size = 2 * r;
    ctx.rect(-r, -r, size, size);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        _one_x(ctx, r);
        ctx.stroke();
    }
};
triangle = function (ctx, i, sx, sy, r, line, fill) {
    _one_tri(ctx, r);
    if (fill.doit) {
        fill.set_vectorize(ctx, i);
        ctx.fill();
    }
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
};
x = function (ctx, i, sx, sy, r, line, fill) {
    _one_x(ctx, r);
    if (line.doit) {
        line.set_vectorize(ctx, i);
        ctx.stroke();
    }
};
_mk_model = function (type, f) {
    var model, view;
    view = (function (superClass) {
        extend(view, superClass);
        function view() {
            return view.__super__.constructor.apply(this, arguments);
        }
        view.prototype._render_one = f;
        return view;
    })(marker_1.MarkerView);
    model = (function (superClass) {
        extend(model, superClass);
        function model() {
            return model.__super__.constructor.apply(this, arguments);
        }
        model.prototype.default_view = view;
        model.prototype.type = type;
        return model;
    })(marker_1.Marker);
    return model;
};
exports.Asterisk = _mk_model('Asterisk', asterisk);
exports.CircleCross = _mk_model('CircleCross', circle_cross);
exports.CircleX = _mk_model('CircleX', circle_x);
exports.Cross = _mk_model('Cross', cross);
exports.Diamond = _mk_model('Diamond', diamond);
exports.DiamondCross = _mk_model('DiamondCross', diamond_cross);
exports.InvertedTriangle = _mk_model('InvertedTriangle', inverted_triangle);
exports.Square = _mk_model('Square', square);
exports.SquareCross = _mk_model('SquareCross', square_cross);
exports.SquareX = _mk_model('SquareX', square_x);
exports.Triangle = _mk_model('Triangle', triangle);
exports.X = _mk_model('X', x);
