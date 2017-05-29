var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  Model
} from "../../model";

import {
  logger
} from "core/logging";

import * as p from "core/properties";

export var ToolEvents = (function(superClass) {
  extend(ToolEvents, superClass);

  function ToolEvents() {
    return ToolEvents.__super__.constructor.apply(this, arguments);
  }

  ToolEvents.prototype.type = 'ToolEvents';

  ToolEvents.define({
    geometries: [p.Array, []]
  });

  return ToolEvents;

})(Model);
