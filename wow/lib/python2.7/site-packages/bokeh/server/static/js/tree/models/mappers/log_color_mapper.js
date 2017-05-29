"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var log1p, ref, extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var p = require("core/properties");
var color_1 = require("core/util/color");
var array_1 = require("core/util/array");
var color_mapper_1 = require("./color_mapper");
log1p = (ref = Math.log1p) != null ? ref : function (x) {
    return Math.log(1 + x);
};
exports.LogColorMapper = (function (superClass) {
    extend(LogColorMapper, superClass);
    function LogColorMapper() {
        return LogColorMapper.__super__.constructor.apply(this, arguments);
    }
    LogColorMapper.prototype.type = "LogColorMapper";
    LogColorMapper.define({
        high: [p.Number],
        low: [p.Number],
        high_color: [p.Color],
        low_color: [p.Color]
    });
    LogColorMapper.prototype.initialize = function (attrs, options) {
        LogColorMapper.__super__.initialize.call(this, attrs, options);
        this._nan_color = this._build_palette([color_1.color2hex(this.nan_color)])[0];
        this._high_color = this.high_color != null ? this._build_palette([color_1.color2hex(this.high_color)])[0] : void 0;
        return this._low_color = this.low_color != null ? this._build_palette([color_1.color2hex(this.low_color)])[0] : void 0;
    };
    LogColorMapper.prototype._get_values = function (data, palette, image_glyph) {
        var d, high, high_color, i, key, len, log, low, low_color, max_key, n, nan_color, ref1, ref2, scale, values;
        if (image_glyph == null) {
            image_glyph = false;
        }
        n = palette.length;
        low = (ref1 = this.low) != null ? ref1 : array_1.min(data);
        high = (ref2 = this.high) != null ? ref2 : array_1.max(data);
        scale = n / (log1p(high) - log1p(low));
        max_key = palette.length - 1;
        values = [];
        nan_color = image_glyph ? this._nan_color : this.nan_color;
        high_color = image_glyph ? this._high_color : this.high_color;
        low_color = image_glyph ? this._low_color : this.low_color;
        for (i = 0, len = data.length; i < len; i++) {
            d = data[i];
            if (isNaN(d)) {
                values.push(nan_color);
                continue;
            }
            if (d > high) {
                if (this.high_color != null) {
                    values.push(high_color);
                }
                else {
                    values.push(palette[max_key]);
                }
                continue;
            }
            if (d === high) {
                values.push(palette[max_key]);
                continue;
            }
            if (d < low) {
                if (this.low_color != null) {
                    values.push(low_color);
                }
                else {
                    values.push(palette[0]);
                }
                continue;
            }
            log = log1p(d) - log1p(low);
            key = Math.floor(log * scale);
            if (key > max_key) {
                key = max_key;
            }
            values.push(palette[key]);
        }
        return values;
    };
    return LogColorMapper;
})(color_mapper_1.ColorMapper);
