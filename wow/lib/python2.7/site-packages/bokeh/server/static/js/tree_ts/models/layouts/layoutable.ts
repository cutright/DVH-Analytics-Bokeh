var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  Model,
  View
} from "../../model";

export var LayoutableView = (function(superClass) {
  extend(LayoutableView, superClass);

  function LayoutableView() {
    return LayoutableView.__super__.constructor.apply(this, arguments);
  }

  return LayoutableView;

})(View);

export var Layoutable = (function(superClass) {
  extend(Layoutable, superClass);

  function Layoutable() {
    return Layoutable.__super__.constructor.apply(this, arguments);
  }

  Layoutable.prototype.type = "Layoutable";

  return Layoutable;

})(Model);
