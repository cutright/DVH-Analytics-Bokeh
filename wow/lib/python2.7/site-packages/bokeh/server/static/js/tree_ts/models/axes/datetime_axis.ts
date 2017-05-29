var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  LinearAxis,
  LinearAxisView
} from "./linear_axis";

import {
  DatetimeTickFormatter
} from "../formatters/datetime_tick_formatter";

import {
  DatetimeTicker
} from "../tickers/datetime_ticker";

export var DatetimeAxisView = (function(superClass) {
  extend(DatetimeAxisView, superClass);

  function DatetimeAxisView() {
    return DatetimeAxisView.__super__.constructor.apply(this, arguments);
  }

  return DatetimeAxisView;

})(LinearAxisView);

export var DatetimeAxis = (function(superClass) {
  extend(DatetimeAxis, superClass);

  function DatetimeAxis() {
    return DatetimeAxis.__super__.constructor.apply(this, arguments);
  }

  DatetimeAxis.prototype.default_view = DatetimeAxisView;

  DatetimeAxis.prototype.type = 'DatetimeAxis';

  DatetimeAxis.override({
    ticker: function() {
      return new DatetimeTicker();
    },
    formatter: function() {
      return new DatetimeTickFormatter();
    }
  });

  return DatetimeAxis;

})(LinearAxis);
