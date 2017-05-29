"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var basic_tick_formatter_1 = require("./basic_tick_formatter");
var p = require("core/properties");
var proj4_1 = require("core/util/proj4");
exports.MercatorTickFormatter = (function (superClass) {
    extend(MercatorTickFormatter, superClass);
    function MercatorTickFormatter() {
        return MercatorTickFormatter.__super__.constructor.apply(this, arguments);
    }
    MercatorTickFormatter.prototype.type = 'MercatorTickFormatter';
    MercatorTickFormatter.define({
        dimension: [p.LatLon]
    });
    MercatorTickFormatter.prototype.doFormat = function (ticks, loc) {
        var i, j, k, lat, lon, proj_ticks, ref, ref1, ref2, ref3;
        if (this.dimension == null) {
            throw new Error("MercatorTickFormatter.dimension not configured");
        }
        if (ticks.length === 0) {
            return [];
        }
        proj_ticks = new Array(ticks.length);
        if (this.dimension === "lon") {
            for (i = j = 0, ref = ticks.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
                ref1 = proj4_1.proj4(proj4_1.mercator).inverse([ticks[i], loc]), lon = ref1[0], lat = ref1[1];
                proj_ticks[i] = lon;
            }
        }
        else {
            for (i = k = 0, ref2 = ticks.length; 0 <= ref2 ? k < ref2 : k > ref2; i = 0 <= ref2 ? ++k : --k) {
                ref3 = proj4_1.proj4(proj4_1.mercator).inverse([loc, ticks[i]]), lon = ref3[0], lat = ref3[1];
                proj_ticks[i] = lat;
            }
        }
        return MercatorTickFormatter.__super__.doFormat.call(this, proj_ticks, loc);
    };
    return MercatorTickFormatter;
})(basic_tick_formatter_1.BasicTickFormatter);
