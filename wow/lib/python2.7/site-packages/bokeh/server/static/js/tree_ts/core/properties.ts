var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty,
  indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

import {
  Events
} from "./events";

import * as enums from "./enums";

import * as svg_colors from "./util/svg_colors";

import {
  valid_rgb
} from "./util/color";

import {
  copy
} from "./util/array";

import {
  isBoolean,
  isNumber,
  isString,
  isFunction,
  isArray,
  isObject
} from "./util/types";

export var Property = (function() {
  extend(Property.prototype, Events);

  Property.prototype.dataspec = false;

  function Property(arg) {
    this.obj = arg.obj, this.attr = arg.attr, this.default_value = arg.default_value;
    this._init(false);
    this.listenTo(this.obj, "change:" + this.attr, (function(_this) {
      return function() {
        _this._init();
        return _this.obj.trigger("propchange");
      };
    })(this));
  }

  Property.prototype.update = function() {
    return this._init();
  };

  Property.prototype.init = function() {};

  Property.prototype.transform = function(values) {
    return values;
  };

  Property.prototype.validate = function(value) {};

  Property.prototype.value = function(do_spec_transform) {
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

  Property.prototype.array = function(source) {
    var data, i, length, ret, value;
    if (!this.dataspec) {
      throw new Error("attempted to retrieve property array for non-dataspec property");
    }
    data = source.data;
    if (this.spec.field != null) {
      if (this.spec.field in data) {
        ret = this.transform(source.get_column(this.spec.field));
      } else {
        throw new Error("attempted to retrieve property array for nonexistent field '" + this.spec.field + "'");
      }
    } else {
      length = source.get_length();
      if (length == null) {
        length = 1;
      }
      value = this.value(false);
      ret = (function() {
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

  Property.prototype._init = function(trigger) {
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
      attr_value = (function() {
        switch (false) {
          case default_value !== void 0:
            return null;
          case !isArray(default_value):
            return copy(default_value);
          case !isFunction(default_value):
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
    if (isArray(attr_value)) {
      this.spec = {
        value: attr_value
      };
    } else if (isObject(attr_value) && ((attr_value.value === void 0) !== (attr_value.field === void 0))) {
      this.spec = attr_value;
    } else {
      this.spec = {
        value: attr_value
      };
    }
    if ((this.spec.field != null) && !isString(this.spec.field)) {
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

export var simple_prop = function(name, pred) {
  var Prop;
  return Prop = (function(superClass) {
    extend(Prop, superClass);

    function Prop() {
      return Prop.__super__.constructor.apply(this, arguments);
    }

    Prop.prototype.toString = function() {
      return name + "(obj: " + this.obj.id + ", spec: " + (JSON.stringify(this.spec)) + ")";
    };

    Prop.prototype.validate = function(value) {
      if (!pred(value)) {
        throw new Error(name + " property '" + this.attr + "' given invalid value: " + (JSON.stringify(value)));
      }
    };

    return Prop;

  })(Property);
};

export var Any = (function(superClass) {
  extend(Any, superClass);

  function Any() {
    return Any.__super__.constructor.apply(this, arguments);
  }

  return Any;

})(simple_prop("Any", function(x) {
  return true;
}));

export var Array = (function(superClass) {
  extend(Array, superClass);

  function Array() {
    return Array.__super__.constructor.apply(this, arguments);
  }

  return Array;

})(simple_prop("Array", function(x) {
  return isArray(x) || x instanceof Float64Array;
}));

export var Bool = (function(superClass) {
  extend(Bool, superClass);

  function Bool() {
    return Bool.__super__.constructor.apply(this, arguments);
  }

  return Bool;

})(simple_prop("Bool", isBoolean));

export var Boolean = Bool;

export var Color = (function(superClass) {
  extend(Color, superClass);

  function Color() {
    return Color.__super__.constructor.apply(this, arguments);
  }

  return Color;

})(simple_prop("Color", function(x) {
  return (svg_colors[x.toLowerCase()] != null) || x.substring(0, 1) === "#" || valid_rgb(x);
}));

export var Instance = (function(superClass) {
  extend(Instance, superClass);

  function Instance() {
    return Instance.__super__.constructor.apply(this, arguments);
  }

  return Instance;

})(simple_prop("Instance", function(x) {
  return x.properties != null;
}));

export var Number = (function(superClass) {
  extend(Number, superClass);

  function Number() {
    return Number.__super__.constructor.apply(this, arguments);
  }

  return Number;

})(simple_prop("Number", function(x) {
  return isNumber(x) || isBoolean(x);
}));

export var Int = Number;

export var Percent = (function(superClass) {
  extend(Percent, superClass);

  function Percent() {
    return Percent.__super__.constructor.apply(this, arguments);
  }

  return Percent;

})(simple_prop("Number", function(x) {
  return (isNumber(x) || isBoolean(x)) && ((0 <= x && x <= 1.0));
}));

export var String = (function(superClass) {
  extend(String, superClass);

  function String() {
    return String.__super__.constructor.apply(this, arguments);
  }

  return String;

})(simple_prop("String", isString));

export var Font = (function(superClass) {
  extend(Font, superClass);

  function Font() {
    return Font.__super__.constructor.apply(this, arguments);
  }

  return Font;

})(String);

export var enum_prop = function(name, enum_values) {
  var Enum;
  return Enum = (function(superClass) {
    extend(Enum, superClass);

    function Enum() {
      return Enum.__super__.constructor.apply(this, arguments);
    }

    Enum.prototype.toString = function() {
      return name + "(obj: " + this.obj.id + ", spec: " + (JSON.stringify(this.spec)) + ")";
    };

    return Enum;

  })(simple_prop(name, function(x) {
    return indexOf.call(enum_values, x) >= 0;
  }));
};

export var Anchor = (function(superClass) {
  extend(Anchor, superClass);

  function Anchor() {
    return Anchor.__super__.constructor.apply(this, arguments);
  }

  return Anchor;

})(enum_prop("Anchor", enums.LegendLocation));

export var AngleUnits = (function(superClass) {
  extend(AngleUnits, superClass);

  function AngleUnits() {
    return AngleUnits.__super__.constructor.apply(this, arguments);
  }

  return AngleUnits;

})(enum_prop("AngleUnits", enums.AngleUnits));

export var Direction = (function(superClass) {
  extend(Direction, superClass);

  function Direction() {
    return Direction.__super__.constructor.apply(this, arguments);
  }

  Direction.prototype.transform = function(values) {
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

})(enum_prop("Direction", enums.Direction));

export var Dimension = (function(superClass) {
  extend(Dimension, superClass);

  function Dimension() {
    return Dimension.__super__.constructor.apply(this, arguments);
  }

  return Dimension;

})(enum_prop("Dimension", enums.Dimension));

export var Dimensions = (function(superClass) {
  extend(Dimensions, superClass);

  function Dimensions() {
    return Dimensions.__super__.constructor.apply(this, arguments);
  }

  return Dimensions;

})(enum_prop("Dimensions", enums.Dimensions));

export var FontStyle = (function(superClass) {
  extend(FontStyle, superClass);

  function FontStyle() {
    return FontStyle.__super__.constructor.apply(this, arguments);
  }

  return FontStyle;

})(enum_prop("FontStyle", enums.FontStyle));

export var LatLon = (function(superClass) {
  extend(LatLon, superClass);

  function LatLon() {
    return LatLon.__super__.constructor.apply(this, arguments);
  }

  return LatLon;

})(enum_prop("LatLon", enums.LatLon));

export var LineCap = (function(superClass) {
  extend(LineCap, superClass);

  function LineCap() {
    return LineCap.__super__.constructor.apply(this, arguments);
  }

  return LineCap;

})(enum_prop("LineCap", enums.LineCap));

export var LineJoin = (function(superClass) {
  extend(LineJoin, superClass);

  function LineJoin() {
    return LineJoin.__super__.constructor.apply(this, arguments);
  }

  return LineJoin;

})(enum_prop("LineJoin", enums.LineJoin));

export var LegendLocation = (function(superClass) {
  extend(LegendLocation, superClass);

  function LegendLocation() {
    return LegendLocation.__super__.constructor.apply(this, arguments);
  }

  return LegendLocation;

})(enum_prop("LegendLocation", enums.LegendLocation));

export var Location = (function(superClass) {
  extend(Location, superClass);

  function Location() {
    return Location.__super__.constructor.apply(this, arguments);
  }

  return Location;

})(enum_prop("Location", enums.Location));

export var Orientation = (function(superClass) {
  extend(Orientation, superClass);

  function Orientation() {
    return Orientation.__super__.constructor.apply(this, arguments);
  }

  return Orientation;

})(enum_prop("Orientation", enums.Orientation));

export var TextAlign = (function(superClass) {
  extend(TextAlign, superClass);

  function TextAlign() {
    return TextAlign.__super__.constructor.apply(this, arguments);
  }

  return TextAlign;

})(enum_prop("TextAlign", enums.TextAlign));

export var TextBaseline = (function(superClass) {
  extend(TextBaseline, superClass);

  function TextBaseline() {
    return TextBaseline.__super__.constructor.apply(this, arguments);
  }

  return TextBaseline;

})(enum_prop("TextBaseline", enums.TextBaseline));

export var RenderLevel = (function(superClass) {
  extend(RenderLevel, superClass);

  function RenderLevel() {
    return RenderLevel.__super__.constructor.apply(this, arguments);
  }

  return RenderLevel;

})(enum_prop("RenderLevel", enums.RenderLevel));

export var RenderMode = (function(superClass) {
  extend(RenderMode, superClass);

  function RenderMode() {
    return RenderMode.__super__.constructor.apply(this, arguments);
  }

  return RenderMode;

})(enum_prop("RenderMode", enums.RenderMode));

export var SizingMode = (function(superClass) {
  extend(SizingMode, superClass);

  function SizingMode() {
    return SizingMode.__super__.constructor.apply(this, arguments);
  }

  return SizingMode;

})(enum_prop("SizingMode", enums.SizingMode));

export var SpatialUnits = (function(superClass) {
  extend(SpatialUnits, superClass);

  function SpatialUnits() {
    return SpatialUnits.__super__.constructor.apply(this, arguments);
  }

  return SpatialUnits;

})(enum_prop("SpatialUnits", enums.SpatialUnits));

export var Distribution = (function(superClass) {
  extend(Distribution, superClass);

  function Distribution() {
    return Distribution.__super__.constructor.apply(this, arguments);
  }

  return Distribution;

})(enum_prop("Distribution", enums.DistributionTypes));

export var TransformStepMode = (function(superClass) {
  extend(TransformStepMode, superClass);

  function TransformStepMode() {
    return TransformStepMode.__super__.constructor.apply(this, arguments);
  }

  return TransformStepMode;

})(enum_prop("TransformStepMode", enums.TransformStepModes));

export var units_prop = function(name, valid_units, default_units) {
  var UnitsProp;
  return UnitsProp = (function(superClass) {
    extend(UnitsProp, superClass);

    function UnitsProp() {
      return UnitsProp.__super__.constructor.apply(this, arguments);
    }

    UnitsProp.prototype.toString = function() {
      return name + "(obj: " + this.obj.id + ", spec: " + (JSON.stringify(this.spec)) + ")";
    };

    UnitsProp.prototype.init = function() {
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

  })(Number);
};

export var Angle = (function(superClass) {
  extend(Angle, superClass);

  function Angle() {
    return Angle.__super__.constructor.apply(this, arguments);
  }

  Angle.prototype.transform = function(values) {
    var x;
    if (this.spec.units === "deg") {
      values = (function() {
        var j, len, results;
        results = [];
        for (j = 0, len = values.length; j < len; j++) {
          x = values[j];
          results.push(x * Math.PI / 180.0);
        }
        return results;
      })();
    }
    values = (function() {
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

})(units_prop("Angle", enums.AngleUnits, "rad"));

export var Distance = (function(superClass) {
  extend(Distance, superClass);

  function Distance() {
    return Distance.__super__.constructor.apply(this, arguments);
  }

  return Distance;

})(units_prop("Distance", enums.SpatialUnits, "data"));

export var AngleSpec = (function(superClass) {
  extend(AngleSpec, superClass);

  function AngleSpec() {
    return AngleSpec.__super__.constructor.apply(this, arguments);
  }

  AngleSpec.prototype.dataspec = true;

  return AngleSpec;

})(Angle);

export var ColorSpec = (function(superClass) {
  extend(ColorSpec, superClass);

  function ColorSpec() {
    return ColorSpec.__super__.constructor.apply(this, arguments);
  }

  ColorSpec.prototype.dataspec = true;

  return ColorSpec;

})(Color);

export var DirectionSpec = (function(superClass) {
  extend(DirectionSpec, superClass);

  function DirectionSpec() {
    return DirectionSpec.__super__.constructor.apply(this, arguments);
  }

  DirectionSpec.prototype.dataspec = true;

  return DirectionSpec;

})(Distance);

export var DistanceSpec = (function(superClass) {
  extend(DistanceSpec, superClass);

  function DistanceSpec() {
    return DistanceSpec.__super__.constructor.apply(this, arguments);
  }

  DistanceSpec.prototype.dataspec = true;

  return DistanceSpec;

})(Distance);

export var FontSizeSpec = (function(superClass) {
  extend(FontSizeSpec, superClass);

  function FontSizeSpec() {
    return FontSizeSpec.__super__.constructor.apply(this, arguments);
  }

  FontSizeSpec.prototype.dataspec = true;

  return FontSizeSpec;

})(String);

export var NumberSpec = (function(superClass) {
  extend(NumberSpec, superClass);

  function NumberSpec() {
    return NumberSpec.__super__.constructor.apply(this, arguments);
  }

  NumberSpec.prototype.dataspec = true;

  return NumberSpec;

})(Number);

export var StringSpec = (function(superClass) {
  extend(StringSpec, superClass);

  function StringSpec() {
    return StringSpec.__super__.constructor.apply(this, arguments);
  }

  StringSpec.prototype.dataspec = true;

  return StringSpec;

})(String);
