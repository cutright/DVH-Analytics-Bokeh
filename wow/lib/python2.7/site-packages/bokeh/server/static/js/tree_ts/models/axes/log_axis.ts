var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  AxisView
} from "./axis";

import {
  ContinuousAxis
} from "./continuous_axis";

import {
  LogTickFormatter
} from "../formatters/log_tick_formatter";

import {
  LogTicker
} from "../tickers/log_ticker";

export var LogAxisView = (function(superClass) {
  extend(LogAxisView, superClass);

  function LogAxisView() {
    return LogAxisView.__super__.constructor.apply(this, arguments);
  }

  return LogAxisView;

})(AxisView);

export var LogAxis = (function(superClass) {
  extend(LogAxis, superClass);

  function LogAxis() {
    return LogAxis.__super__.constructor.apply(this, arguments);
  }

  LogAxis.prototype.default_view = LogAxisView;

  LogAxis.prototype.type = 'LogAxis';

  LogAxis.override({
    ticker: function() {
      return new LogTicker();
    },
    formatter: function() {
      return new LogTickFormatter();
    }
  });

  return LogAxis;

})(ContinuousAxis);
