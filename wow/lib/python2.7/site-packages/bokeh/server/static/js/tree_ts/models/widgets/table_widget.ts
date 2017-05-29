var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  Widget
} from "./widget";

import * as p from "core/properties";

export var TableWidget = (function(superClass) {
  extend(TableWidget, superClass);

  function TableWidget() {
    return TableWidget.__super__.constructor.apply(this, arguments);
  }

  TableWidget.prototype.type = "TableWidget";

  TableWidget.define({
    source: [p.Instance]
  });

  return TableWidget;

})(Widget);
