var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  AxisView
} from "./axis";

import {
  ContinuousAxis
} from "./continuous_axis";

import {
  BasicTickFormatter
} from "../formatters/basic_tick_formatter";

import {
  BasicTicker
} from "../tickers/basic_ticker";

export var LinearAxisView = (function(superClass) {
  extend(LinearAxisView, superClass);

  function LinearAxisView() {
    return LinearAxisView.__super__.constructor.apply(this, arguments);
  }

  return LinearAxisView;

})(AxisView);

export var LinearAxis = (function(superClass) {
  extend(LinearAxis, superClass);

  function LinearAxis() {
    return LinearAxis.__super__.constructor.apply(this, arguments);
  }

  LinearAxis.prototype.default_view = LinearAxisView;

  LinearAxis.prototype.type = 'LinearAxis';

  LinearAxis.override({
    ticker: function() {
      return new BasicTicker();
    },
    formatter: function() {
      return new BasicTickFormatter();
    }
  });

  return LinearAxis;

})(ContinuousAxis);
