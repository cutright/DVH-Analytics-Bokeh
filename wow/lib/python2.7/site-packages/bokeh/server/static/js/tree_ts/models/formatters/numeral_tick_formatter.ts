var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import * as Numbro from "numbro";

import {
  TickFormatter
} from "./tick_formatter";

import * as p from "core/properties";

export var NumeralTickFormatter = (function(superClass) {
  extend(NumeralTickFormatter, superClass);

  function NumeralTickFormatter() {
    return NumeralTickFormatter.__super__.constructor.apply(this, arguments);
  }

  NumeralTickFormatter.prototype.type = 'NumeralTickFormatter';

  NumeralTickFormatter.define({
    format: [p.String, '0,0'],
    language: [p.String, 'en'],
    rounding: [p.String, 'round']
  });

  NumeralTickFormatter.prototype.doFormat = function(ticks, loc) {
    var format, labels, language, rounding, tick;
    format = this.format;
    language = this.language;
    rounding = (function() {
      switch (this.rounding) {
        case "round":
        case "nearest":
          return Math.round;
        case "floor":
        case "rounddown":
          return Math.floor;
        case "ceil":
        case "roundup":
          return Math.ceil;
      }
    }).call(this);
    labels = (function() {
      var i, len, results;
      results = [];
      for (i = 0, len = ticks.length; i < len; i++) {
        tick = ticks[i];
        results.push(Numbro.format(tick, format, language, rounding));
      }
      return results;
    })();
    return labels;
  };

  return NumeralTickFormatter;

})(TickFormatter);
