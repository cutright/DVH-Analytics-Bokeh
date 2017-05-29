var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  AdaptiveTicker
} from "./adaptive_ticker";

export var BasicTicker = (function(superClass) {
  extend(BasicTicker, superClass);

  function BasicTicker() {
    return BasicTicker.__super__.constructor.apply(this, arguments);
  }

  BasicTicker.prototype.type = 'BasicTicker';

  return BasicTicker;

})(AdaptiveTicker);
