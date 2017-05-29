var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  Model
} from "../../model";

export var Transform = (function(superClass) {
  extend(Transform, superClass);

  function Transform() {
    return Transform.__super__.constructor.apply(this, arguments);
  }

  return Transform;

})(Model);
