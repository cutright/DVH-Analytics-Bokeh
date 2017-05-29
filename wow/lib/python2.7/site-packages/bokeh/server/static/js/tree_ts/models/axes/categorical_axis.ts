var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  Axis,
  AxisView
} from "./axis";

import {
  CategoricalTickFormatter
} from "../formatters/categorical_tick_formatter";

import {
  CategoricalTicker
} from "../tickers/categorical_ticker";

import {
  logger
} from "core/logging";

export var CategoricalAxisView = (function(superClass) {
  extend(CategoricalAxisView, superClass);

  function CategoricalAxisView() {
    return CategoricalAxisView.__super__.constructor.apply(this, arguments);
  }

  return CategoricalAxisView;

})(AxisView);

export var CategoricalAxis = (function(superClass) {
  extend(CategoricalAxis, superClass);

  function CategoricalAxis() {
    return CategoricalAxis.__super__.constructor.apply(this, arguments);
  }

  CategoricalAxis.prototype.default_view = CategoricalAxisView;

  CategoricalAxis.prototype.type = 'CategoricalAxis';

  CategoricalAxis.override({
    ticker: function() {
      return new CategoricalTicker();
    },
    formatter: function() {
      return new CategoricalTickFormatter();
    }
  });

  CategoricalAxis.prototype._computed_bounds = function() {
    var cross_range, range, range_bounds, ref, ref1, user_bounds;
    ref = this.ranges, range = ref[0], cross_range = ref[1];
    user_bounds = (ref1 = this.bounds) != null ? ref1 : 'auto';
    range_bounds = [range.min, range.max];
    if (user_bounds !== 'auto') {
      logger.warn("Categorical Axes only support user_bounds='auto', ignoring");
    }
    return range_bounds;
  };

  return CategoricalAxis;

})(Axis);
