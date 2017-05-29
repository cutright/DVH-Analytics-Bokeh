"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var proj4_1 = require("./proj4");
exports.project_xy = function (x, y) {
    var i, j, merc_x, merc_x_s, merc_y, merc_y_s, ref, ref1;
    merc_x_s = [];
    merc_y_s = [];
    for (i = j = 0, ref = x.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
        ref1 = proj4_1.proj4(proj4_1.mercator, [x[i], y[i]]), merc_x = ref1[0], merc_y = ref1[1];
        merc_x_s[i] = merc_x;
        merc_y_s[i] = merc_y;
    }
    return [merc_x_s, merc_y_s];
};
exports.project_xsys = function (xs, ys) {
    var i, j, merc_x_s, merc_xs_s, merc_y_s, merc_ys_s, ref, ref1;
    merc_xs_s = [];
    merc_ys_s = [];
    for (i = j = 0, ref = xs.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
        ref1 = exports.project_xy(xs[i], ys[i]), merc_x_s = ref1[0], merc_y_s = ref1[1];
        merc_xs_s[i] = merc_x_s;
        merc_ys_s[i] = merc_y_s;
    }
    return [merc_xs_s, merc_ys_s];
};
