var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import * as SPrintf from "sprintf";

import {
  TickFormatter
} from "./tick_formatter";

import * as p from "core/properties";

export var PrintfTickFormatter = (function(superClass) {
  extend(PrintfTickFormatter, superClass);

  function PrintfTickFormatter() {
    return PrintfTickFormatter.__super__.constructor.apply(this, arguments);
  }

  PrintfTickFormatter.prototype.type = 'PrintfTickFormatter';

  PrintfTickFormatter.define({
    format: [p.String, '%s']
  });

  PrintfTickFormatter.prototype.doFormat = function(ticks, loc) {
    var format, labels, tick;
    format = this.format;
    labels = (function() {
      var i, len, results;
      results = [];
      for (i = 0, len = ticks.length; i < len; i++) {
        tick = ticks[i];
        results.push(SPrintf.sprintf(format, tick));
      }
      return results;
    })();
    return labels;
  };

  return PrintfTickFormatter;

})(TickFormatter);
