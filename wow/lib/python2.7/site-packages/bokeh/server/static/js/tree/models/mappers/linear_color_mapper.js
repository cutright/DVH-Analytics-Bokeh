"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var p = require("core/properties");
var color_1 = require("core/util/color");
var array_1 = require("core/util/array");
var color_mapper_1 = require("./color_mapper");
exports.LinearColorMapper = (function (superClass) {
    extend(LinearColorMapper, superClass);
    function LinearColorMapper() {
        return LinearColorMapper.__super__.constructor.apply(this, arguments);
    }
    LinearColorMapper.prototype.type = "LinearColorMapper";
    LinearColorMapper.define({
        high: [p.Number],
        low: [p.Number],
        high_color: [p.Color],
        low_color: [p.Color]
    });
    LinearColorMapper.prototype.initialize = function (attrs, options) {
        LinearColorMapper.__super__.initialize.call(this, attrs, options);
        this._nan_color = this._build_palette([color_1.color2hex(this.nan_color)])[0];
        this._high_color = this.high_color != null ? this._build_palette([color_1.color2hex(this.high_color)])[0] : void 0;
        return this._low_color = this.low_color != null ? this._build_palette([color_1.color2hex(this.low_color)])[0] : void 0;
    };
    LinearColorMapper.prototype._get_values = function (data, palette, image_glyph) {
        var d, high, high_color, i, key, len, low, low_color, max_key, nan_color, norm_factor, normed_d, normed_interval, ref, ref1, values;
        if (image_glyph == null) {
            image_glyph = false;
        }
        low = (ref = this.low) != null ? ref : array_1.min(data);
        high = (ref1 = this.high) != null ? ref1 : array_1.max(data);
        max_key = palette.length - 1;
        values = [];
        nan_color = image_glyph ? this._nan_color : this.nan_color;
        low_color = image_glyph ? this._low_color : this.low_color;
        high_color = image_glyph ? this._high_color : this.high_color;
        norm_factor = 1 / (high - low);
        normed_interval = 1 / palette.length;
        for (i = 0, len = data.length; i < len; i++) {
            d = data[i];
            if (isNaN(d)) {
                values.push(nan_color);
                continue;
            }
            if (d === high) {
                values.push(palette[max_key]);
                continue;
            }
            normed_d = (d - low) * norm_factor;
            key = Math.floor(normed_d / normed_interval);
            if (key < 0) {
                if (this.low_color != null) {
                    values.push(low_color);
                }
                else {
                    values.push(palette[0]);
                }
            }
            else if (key > max_key) {
                if (this.high_color != null) {
                    values.push(high_color);
                }
                else {
                    values.push(palette[max_key]);
                }
            }
            else {
                values.push(palette[key]);
            }
        }
        return values;
    };
    return LinearColorMapper;
})(color_mapper_1.ColorMapper);
