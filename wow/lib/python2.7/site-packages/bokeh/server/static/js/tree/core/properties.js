"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty, indexOf = [].indexOf || function (item) { for (var i = 0, l = this.length; i < l; i++) {
    if (i in this && this[i] === item)
        return i;
} return -1; };
var events_1 = require("./events");
var enums = require("./enums");
var svg_colors = require("./util/svg_colors");
var color_1 = require("./util/color");
var array_1 = require("./util/array");
var types_1 = require("./util/types");
exports.Property = (function () {
    extend(Property.prototype, events_1.Events);
    Property.prototype.dataspec = false;
    function Property(arg) {
        this.obj = arg.obj, this.attr = arg.attr, this.default_value = arg.default_value;
        this._init(false);
        this.listenTo(this.obj, "change:" + this.attr, (function (_this) {
            return function () {
                _this._init();
                return _this.obj.trigger("propchange");
            };
        })(this));
    }
    Property.prototype.update = function () {
        return this._init();
    };
    Property.prototype.init = function () { };
    Property.prototype.transform = function (values) {
        return values;
    };
    Property.prototype.validate = function (value) { };
    Property.prototype.value = function (do_spec_transform) {
        var ret;
        if (do_spec_transform == null) {
            do_spec_transform = true;
        }
        if (this.spec.value === void 0) {
            throw new Error("attempted to retrieve property value for property without value specification");
        }
        ret = this.transform([this.spec.value])[0];
        if ((this.spec.transform != null) && do_spec_transform) {
            ret = this.spec.transform.compute(ret);
        }
        return ret;
    };
    Property.prototype.array = function (source) {
        var data, i, length, ret, value;
        if (!this.dataspec) {
            throw new Error("attempted to retrieve property array for non-dataspec property");
        }
        data = source.data;
        if (this.spec.field != null) {
            if (this.spec.field in data) {
                ret = this.transform(source.get_column(this.spec.field));
            }
            else {
                throw new Error("attempted to retrieve property array for nonexistent field '" + this.spec.field + "'");
            }
        }
        else {
            length = source.get_length();
            if (length == null) {
                length = 1;
            }
            value = this.value(false);
            ret = (function () {
                var j, ref, results;
                results = [];
                for (i = j = 0, ref = length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
                    results.push(value);
                }
                return results;
            })();
        }
        if (this.spec.transform != null) {
            ret = this.spec.transform.v_compute(ret);
        }
        return ret;
    };
    Property.prototype._init = function (trigger) {
        var attr, attr_value, default_value, obj;
        if (trigger == null) {
            trigger = true;
        }
        obj = this.obj;
        if (obj == null) {
            throw new Error("missing property object");
        }
        if (obj.properties == null) {
            throw new Error("property object must be a HasProps");
        }
        attr = this.attr;
        if (attr == null) {
            throw new Error("missing property attr");
        }
        attr_value = obj.getv(attr);
        if (attr_value === void 0) {
            default_value = this.default_value;
            attr_value = (function () {
                switch (false) {
                    case default_value !== void 0:
                        return null;
                    case !types_1.isArray(default_value):
                        return array_1.copy(default_value);
                    case !types_1.isFunction(default_value):
                        return default_value(obj);
                    default:
                        return default_value;
                }
            })();
            obj.setv(attr, attr_value, {
                silent: true,
                defaults: true
            });
        }
        if (types_1.isArray(attr_value)) {
            this.spec = {
                value: attr_value
            };
        }
        else if (types_1.isObject(attr_value) && ((attr_value.value === void 0) !== (attr_value.field === void 0))) {
            this.spec = attr_value;
        }
        else {
            this.spec = {
                value: attr_value
            };
        }
        if ((this.spec.field != null) && !types_1.isString(this.spec.field)) {
            throw new Error("field value for property '" + attr + "' is not a string");
        }
        if (this.spec.value != null) {
            this.validate(this.spec.value);
        }
        this.init();
        if (trigger) {
            return this.trigger("change");
        }
    };
    return Property;
})();
exports.simple_prop = function (name, pred) {
    var Prop;
    return Prop = (function (superClass) {
        extend(Prop, superClass);
        function Prop() {
            return Prop.__super__.constructor.apply(this, arguments);
        }
        Prop.prototype.toString = function () {
            return name + "(obj: " + this.obj.id + ", spec: " + (JSON.stringify(this.spec)) + ")";
        };
        Prop.prototype.validate = function (value) {
            if (!pred(value)) {
                throw new Error(name + " property '" + this.attr + "' given invalid value: " + (JSON.stringify(value)));
            }
        };
        return Prop;
    })(exports.Property);
};
exports.Any = (function (superClass) {
    extend(Any, superClass);
    function Any() {
        return Any.__super__.constructor.apply(this, arguments);
    }
    return Any;
})(exports.simple_prop("Any", function (x) {
    return true;
}));
exports.Array = (function (superClass) {
    extend(Array, superClass);
    function Array() {
        return Array.__super__.constructor.apply(this, arguments);
    }
    return Array;
})(exports.simple_prop("Array", function (x) {
    return types_1.isArray(x) || x instanceof Float64Array;
}));
exports.Bool = (function (superClass) {
    extend(Bool, superClass);
    function Bool() {
        return Bool.__super__.constructor.apply(this, arguments);
    }
    return Bool;
})(exports.simple_prop("Bool", types_1.isBoolean));
exports.Boolean = exports.Bool;
exports.Color = (function (superClass) {
    extend(Color, superClass);
    function Color() {
        return Color.__super__.constructor.apply(this, arguments);
    }
    return Color;
})(exports.simple_prop("Color", function (x) {
    return (svg_colors[x.toLowerCase()] != null) || x.substring(0, 1) === "#" || color_1.valid_rgb(x);
}));
exports.Instance = (function (superClass) {
    extend(Instance, superClass);
    function Instance() {
        return Instance.__super__.constructor.apply(this, arguments);
    }
    return Instance;
})(exports.simple_prop("Instance", function (x) {
    return x.properties != null;
}));
exports.Number = (function (superClass) {
    extend(Number, superClass);
    function Number() {
        return Number.__super__.constructor.apply(this, arguments);
    }
    return Number;
})(exports.simple_prop("Number", function (x) {
    return types_1.isNumber(x) || types_1.isBoolean(x);
}));
exports.Int = exports.Number;
exports.Percent = (function (superClass) {
    extend(Percent, superClass);
    function Percent() {
        return Percent.__super__.constructor.apply(this, arguments);
    }
    return Percent;
})(exports.simple_prop("Number", function (x) {
    return (types_1.isNumber(x) || types_1.isBoolean(x)) && ((0 <= x && x <= 1.0));
}));
exports.String = (function (superClass) {
    extend(String, superClass);
    function String() {
        return String.__super__.constructor.apply(this, arguments);
    }
    return String;
})(exports.simple_prop("String", types_1.isString));
exports.Font = (function (superClass) {
    extend(Font, superClass);
    function Font() {
        return Font.__super__.constructor.apply(this, arguments);
    }
    return Font;
})(exports.String);
exports.enum_prop = function (name, enum_values) {
    var Enum;
    return Enum = (function (superClass) {
        extend(Enum, superClass);
        function Enum() {
            return Enum.__super__.constructor.apply(this, arguments);
        }
        Enum.prototype.toString = function () {
            return name + "(obj: " + this.obj.id + ", spec: " + (JSON.stringify(this.spec)) + ")";
        };
        return Enum;
    })(exports.simple_prop(name, function (x) {
        return indexOf.call(enum_values, x) >= 0;
    }));
};
exports.Anchor = (function (superClass) {
    extend(Anchor, superClass);
    function Anchor() {
        return Anchor.__super__.constructor.apply(this, arguments);
    }
    return Anchor;
})(exports.enum_prop("Anchor", enums.LegendLocation));
exports.AngleUnits = (function (superClass) {
    extend(AngleUnits, superClass);
    function AngleUnits() {
        return AngleUnits.__super__.constructor.apply(this, arguments);
    }
    return AngleUnits;
})(exports.enum_prop("AngleUnits", enums.AngleUnits));
exports.Direction = (function (superClass) {
    extend(Direction, superClass);
    function Direction() {
        return Direction.__super__.constructor.apply(this, arguments);
    }
    Direction.prototype.transform = function (values) {
        var i, j, ref, result;
        result = new Uint8Array(values.length);
        for (i = j = 0, ref = values.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
            switch (values[i]) {
                case 'clock':
                    result[i] = false;
                    break;
                case 'anticlock':
                    result[i] = true;
            }
        }
        return result;
    };
    return Direction;
})(exports.enum_prop("Direction", enums.Direction));
exports.Dimension = (function (superClass) {
    extend(Dimension, superClass);
    function Dimension() {
        return Dimension.__super__.constructor.apply(this, arguments);
    }
    return Dimension;
})(exports.enum_prop("Dimension", enums.Dimension));
exports.Dimensions = (function (superClass) {
    extend(Dimensions, superClass);
    function Dimensions() {
        return Dimensions.__super__.constructor.apply(this, arguments);
    }
    return Dimensions;
})(exports.enum_prop("Dimensions", enums.Dimensions));
exports.FontStyle = (function (superClass) {
    extend(FontStyle, superClass);
    function FontStyle() {
        return FontStyle.__super__.constructor.apply(this, arguments);
    }
    return FontStyle;
})(exports.enum_prop("FontStyle", enums.FontStyle));
exports.LatLon = (function (superClass) {
    extend(LatLon, superClass);
    function LatLon() {
        return LatLon.__super__.constructor.apply(this, arguments);
    }
    return LatLon;
})(exports.enum_prop("LatLon", enums.LatLon));
exports.LineCap = (function (superClass) {
    extend(LineCap, superClass);
    function LineCap() {
        return LineCap.__super__.constructor.apply(this, arguments);
    }
    return LineCap;
})(exports.enum_prop("LineCap", enums.LineCap));
exports.LineJoin = (function (superClass) {
    extend(LineJoin, superClass);
    function LineJoin() {
        return LineJoin.__super__.constructor.apply(this, arguments);
    }
    return LineJoin;
})(exports.enum_prop("LineJoin", enums.LineJoin));
exports.LegendLocation = (function (superClass) {
    extend(LegendLocation, superClass);
    function LegendLocation() {
        return LegendLocation.__super__.constructor.apply(this, arguments);
    }
    return LegendLocation;
})(exports.enum_prop("LegendLocation", enums.LegendLocation));
exports.Location = (function (superClass) {
    extend(Location, superClass);
    function Location() {
        return Location.__super__.constructor.apply(this, arguments);
    }
    return Location;
})(exports.enum_prop("Location", enums.Location));
exports.Orientation = (function (superClass) {
    extend(Orientation, superClass);
    function Orientation() {
        return Orientation.__super__.constructor.apply(this, arguments);
    }
    return Orientation;
})(exports.enum_prop("Orientation", enums.Orientation));
exports.TextAlign = (function (superClass) {
    extend(TextAlign, superClass);
    function TextAlign() {
        return TextAlign.__super__.constructor.apply(this, arguments);
    }
    return TextAlign;
})(exports.enum_prop("TextAlign", enums.TextAlign));
exports.TextBaseline = (function (superClass) {
    extend(TextBaseline, superClass);
    function TextBaseline() {
        return TextBaseline.__super__.constructor.apply(this, arguments);
    }
    return TextBaseline;
})(exports.enum_prop("TextBaseline", enums.TextBaseline));
exports.RenderLevel = (function (superClass) {
    extend(RenderLevel, superClass);
    function RenderLevel() {
        return RenderLevel.__super__.constructor.apply(this, arguments);
    }
    return RenderLevel;
})(exports.enum_prop("RenderLevel", enums.RenderLevel));
exports.RenderMode = (function (superClass) {
    extend(RenderMode, superClass);
    function RenderMode() {
        return RenderMode.__super__.constructor.apply(this, arguments);
    }
    return RenderMode;
})(exports.enum_prop("RenderMode", enums.RenderMode));
exports.SizingMode = (function (superClass) {
    extend(SizingMode, superClass);
    function SizingMode() {
        return SizingMode.__super__.constructor.apply(this, arguments);
    }
    return SizingMode;
})(exports.enum_prop("SizingMode", enums.SizingMode));
exports.SpatialUnits = (function (superClass) {
    extend(SpatialUnits, superClass);
    function SpatialUnits() {
        return SpatialUnits.__super__.constructor.apply(this, arguments);
    }
    return SpatialUnits;
})(exports.enum_prop("SpatialUnits", enums.SpatialUnits));
exports.Distribution = (function (superClass) {
    extend(Distribution, superClass);
    function Distribution() {
        return Distribution.__super__.constructor.apply(this, arguments);
    }
    return Distribution;
})(exports.enum_prop("Distribution", enums.DistributionTypes));
exports.TransformStepMode = (function (superClass) {
    extend(TransformStepMode, superClass);
    function TransformStepMode() {
        return TransformStepMode.__super__.constructor.apply(this, arguments);
    }
    return TransformStepMode;
})(exports.enum_prop("TransformStepMode", enums.TransformStepModes));
exports.units_prop = function (name, valid_units, default_units) {
    var UnitsProp;
    return UnitsProp = (function (superClass) {
        extend(UnitsProp, superClass);
        function UnitsProp() {
            return UnitsProp.__super__.constructor.apply(this, arguments);
        }
        UnitsProp.prototype.toString = function () {
            return name + "(obj: " + this.obj.id + ", spec: " + (JSON.stringify(this.spec)) + ")";
        };
        UnitsProp.prototype.init = function () {
            var units;
            if (this.spec.units == null) {
                this.spec.units = default_units;
            }
            this.units = this.spec.units;
            units = this.spec.units;
            if (indexOf.call(valid_units, units) < 0) {
                throw new Error(name + " units must be one of " + valid_units + ", given invalid value: " + units);
            }
        };
        return UnitsProp;
    })(exports.Number);
};
exports.Angle = (function (superClass) {
    extend(Angle, superClass);
    function Angle() {
        return Angle.__super__.constructor.apply(this, arguments);
    }
    Angle.prototype.transform = function (values) {
        var x;
        if (this.spec.units === "deg") {
            values = (function () {
                var j, len, results;
                results = [];
                for (j = 0, len = values.length; j < len; j++) {
                    x = values[j];
                    results.push(x * Math.PI / 180.0);
                }
                return results;
            })();
        }
        values = (function () {
            var j, len, results;
            results = [];
            for (j = 0, len = values.length; j < len; j++) {
                x = values[j];
                results.push(-x);
            }
            return results;
        })();
        return Angle.__super__.transform.call(this, values);
    };
    return Angle;
})(exports.units_prop("Angle", enums.AngleUnits, "rad"));
exports.Distance = (function (superClass) {
    extend(Distance, superClass);
    function Distance() {
        return Distance.__super__.constructor.apply(this, arguments);
    }
    return Distance;
})(exports.units_prop("Distance", enums.SpatialUnits, "data"));
exports.AngleSpec = (function (superClass) {
    extend(AngleSpec, superClass);
    function AngleSpec() {
        return AngleSpec.__super__.constructor.apply(this, arguments);
    }
    AngleSpec.prototype.dataspec = true;
    return AngleSpec;
})(exports.Angle);
exports.ColorSpec = (function (superClass) {
    extend(ColorSpec, superClass);
    function ColorSpec() {
        return ColorSpec.__super__.constructor.apply(this, arguments);
    }
    ColorSpec.prototype.dataspec = true;
    return ColorSpec;
})(exports.Color);
exports.DirectionSpec = (function (superClass) {
    extend(DirectionSpec, superClass);
    function DirectionSpec() {
        return DirectionSpec.__super__.constructor.apply(this, arguments);
    }
    DirectionSpec.prototype.dataspec = true;
    return DirectionSpec;
})(exports.Distance);
exports.DistanceSpec = (function (superClass) {
    extend(DistanceSpec, superClass);
    function DistanceSpec() {
        return DistanceSpec.__super__.constructor.apply(this, arguments);
    }
    DistanceSpec.prototype.dataspec = true;
    return DistanceSpec;
})(exports.Distance);
exports.FontSizeSpec = (function (superClass) {
    extend(FontSizeSpec, superClass);
    function FontSizeSpec() {
        return FontSizeSpec.__super__.constructor.apply(this, arguments);
    }
    FontSizeSpec.prototype.dataspec = true;
    return FontSizeSpec;
})(exports.String);
exports.NumberSpec = (function (superClass) {
    extend(NumberSpec, superClass);
    function NumberSpec() {
        return NumberSpec.__super__.constructor.apply(this, arguments);
    }
    NumberSpec.prototype.dataspec = true;
    return NumberSpec;
})(exports.Number);
exports.StringSpec = (function (superClass) {
    extend(StringSpec, superClass);
    function StringSpec() {
        return StringSpec.__super__.constructor.apply(this, arguments);
    }
    StringSpec.prototype.dataspec = true;
    return StringSpec;
})(exports.String);
