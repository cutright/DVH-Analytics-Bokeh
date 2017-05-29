var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  ContinuousTicker
} from "./continuous_ticker";

import * as p from "core/properties";

export var FixedTicker = (function(superClass) {
  extend(FixedTicker, superClass);

  function FixedTicker() {
    return FixedTicker.__super__.constructor.apply(this, arguments);
  }

  FixedTicker.prototype.type = 'FixedTicker';

  FixedTicker.define({
    ticks: [p.Array, []]
  });

  FixedTicker.prototype.get_ticks_no_defaults = function(data_low, data_high, cross_loc, desired_n_ticks) {
    return {
      major: this.ticks,
      minor: []
    };
  };

  return FixedTicker;

})(ContinuousTicker);
