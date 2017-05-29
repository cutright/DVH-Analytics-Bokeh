"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var math_1 = require("./math");
exports.scale_highlow = function (range, factor, center) {
    var high, low, ref, x, x0, x1;
    if (center == null) {
        center = null;
    }
    ref = [range.start, range.end], low = ref[0], high = ref[1];
    x = center != null ? center : (high + low) / 2.0;
    x0 = low - (low - x) * factor;
    x1 = high - (high - x) * factor;
    return [x0, x1];
};
exports.get_info = function (mappers, arg) {
    var end, info, mapper, name, ref, start, x0, x1;
    x0 = arg[0], x1 = arg[1];
    info = {};
    for (name in mappers) {
        mapper = mappers[name];
        ref = mapper.v_map_from_target([x0, x1], true), start = ref[0], end = ref[1];
        info[name] = {
            start: start,
            end: end
        };
    }
    return info;
};
exports.scale_range = function (frame, factor, h_axis, v_axis, center) {
    var hfactor, ref, ref1, vfactor, vx0, vx1, vy0, vy1, xrs, yrs;
    if (h_axis == null) {
        h_axis = true;
    }
    if (v_axis == null) {
        v_axis = true;
    }
    if (center == null) {
        center = null;
    }
    "Utility function for zoom tools to calculate/create the zoom_info object\nof the form required by ``PlotCanvasView.update_range``\n\nParameters:\n  frame : CartesianFrame\n  factor : Number\n  h_axis : Boolean, optional\n    whether to zoom the horizontal axis (default = true)\n  v_axis : Boolean, optional\n    whether to zoom the horizontal axis (default = true)\n  center : object, optional\n    of form {'x': Number, 'y', Number}\n\nReturns:\n  object:";
    factor = math_1.clamp(factor, -0.9, 0.9);
    hfactor = h_axis ? factor : 0;
    ref = exports.scale_highlow(frame.h_range, hfactor, center != null ? center.x : void 0), vx0 = ref[0], vx1 = ref[1];
    xrs = exports.get_info(frame.x_mappers, [vx0, vx1]);
    vfactor = v_axis ? factor : 0;
    ref1 = exports.scale_highlow(frame.v_range, vfactor, center != null ? center.y : void 0), vy0 = ref1[0], vy1 = ref1[1];
    yrs = exports.get_info(frame.y_mappers, [vy0, vy1]);
    return {
        xrs: xrs,
        yrs: yrs,
        factor: factor
    };
};
