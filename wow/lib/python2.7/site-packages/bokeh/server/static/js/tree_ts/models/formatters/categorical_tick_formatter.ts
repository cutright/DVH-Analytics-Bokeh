var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  TickFormatter
} from "./tick_formatter";

export var CategoricalTickFormatter = (function(superClass) {
  extend(CategoricalTickFormatter, superClass);

  function CategoricalTickFormatter() {
    return CategoricalTickFormatter.__super__.constructor.apply(this, arguments);
  }

  CategoricalTickFormatter.prototype.type = 'CategoricalTickFormatter';

  CategoricalTickFormatter.prototype.doFormat = function(ticks, loc) {
    return ticks;
  };

  return CategoricalTickFormatter;

})(TickFormatter);
