var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  ContinuousTicker
} from "./continuous_ticker";

import * as p from "core/properties";

import {
  argmin,
  sortedIndex
} from "core/util/array";

export var CompositeTicker = (function(superClass) {
  extend(CompositeTicker, superClass);

  function CompositeTicker() {
    return CompositeTicker.__super__.constructor.apply(this, arguments);
  }

  CompositeTicker.prototype.type = 'CompositeTicker';

  CompositeTicker.define({
    tickers: [p.Array, []]
  });

  CompositeTicker.getters({
    min_intervals: function() {
      var i, len, ref, results, ticker;
      ref = this.tickers;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        ticker = ref[i];
        results.push(ticker.get_min_interval());
      }
      return results;
    },
    max_intervals: function() {
      var i, len, ref, results, ticker;
      ref = this.tickers;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        ticker = ref[i];
        results.push(ticker.get_max_interval());
      }
      return results;
    },
    min_interval: function() {
      return this.min_intervals[0];
    },
    max_interval: function() {
      return this.max_intervals[0];
    }
  });

  CompositeTicker.prototype.get_best_ticker = function(data_low, data_high, desired_n_ticks) {
    var best_index, best_ticker, best_ticker_ndx, data_range, errors, ideal_interval, intervals, ticker_ndxs;
    data_range = data_high - data_low;
    ideal_interval = this.get_ideal_interval(data_low, data_high, desired_n_ticks);
    ticker_ndxs = [sortedIndex(this.min_intervals, ideal_interval) - 1, sortedIndex(this.max_intervals, ideal_interval)];
    intervals = [this.min_intervals[ticker_ndxs[0]], this.max_intervals[ticker_ndxs[1]]];
    errors = intervals.map(function(interval) {
      return Math.abs(desired_n_ticks - (data_range / interval));
    });
    best_index = argmin(errors);
    if (best_index === 2e308) {
      return this.tickers[0];
    }
    best_ticker_ndx = ticker_ndxs[best_index];
    best_ticker = this.tickers[best_ticker_ndx];
    return best_ticker;
  };

  CompositeTicker.prototype.get_interval = function(data_low, data_high, desired_n_ticks) {
    var best_ticker;
    best_ticker = this.get_best_ticker(data_low, data_high, desired_n_ticks);
    return best_ticker.get_interval(data_low, data_high, desired_n_ticks);
  };

  CompositeTicker.prototype.get_ticks_no_defaults = function(data_low, data_high, cross_loc, desired_n_ticks) {
    var best_ticker, ticks;
    best_ticker = this.get_best_ticker(data_low, data_high, desired_n_ticks);
    ticks = best_ticker.get_ticks_no_defaults(data_low, data_high, cross_loc, desired_n_ticks);
    return ticks;
  };

  return CompositeTicker;

})(ContinuousTicker);
