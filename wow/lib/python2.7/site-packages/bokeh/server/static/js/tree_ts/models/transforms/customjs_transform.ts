var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty,
  slice = [].slice;

import {
  Transform
} from "./transform";

import * as p from "core/properties";

import {
  values
} from "core/util/object";

export var CustomJSTransform = (function(superClass) {
  extend(CustomJSTransform, superClass);

  function CustomJSTransform() {
    return CustomJSTransform.__super__.constructor.apply(this, arguments);
  }

  CustomJSTransform.prototype.type = 'CustomJSTransform';

  CustomJSTransform.define({
    args: [p.Any, {}],
    func: [p.String, ""],
    v_func: [p.String, ""]
  });

  CustomJSTransform.getters({
    values: function() {
      return this._make_values();
    },
    scalar_transform: function() {
      return this._make_transform("x", this.func);
    },
    vector_transform: function() {
      return this._make_transform("xs", this.v_func);
    }
  });

  CustomJSTransform.prototype.compute = function(x) {
    return this.scalar_transform.apply(this, slice.call(this.values).concat([x], [require], [exports]));
  };

  CustomJSTransform.prototype.v_compute = function(xs) {
    return this.vector_transform.apply(this, slice.call(this.values).concat([xs], [require], [exports]));
  };

  CustomJSTransform.prototype._make_transform = function(val, fn) {
    return (function(func, args, ctor) {
      ctor.prototype = func.prototype;
      var child = new ctor, result = func.apply(child, args);
      return Object(result) === result ? result : child;
    })(Function, slice.call(Object.keys(this.args)).concat([val], ["require"], ["exports"], [fn]), function(){});
  };

  CustomJSTransform.prototype._make_values = function() {
    return values(this.args);
  };

  return CustomJSTransform;

})(Transform);
