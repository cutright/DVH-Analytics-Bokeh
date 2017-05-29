var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  Widget,
  WidgetView
} from "./widget";

import * as p from "core/properties";

export var InputWidgetView = (function(superClass) {
  extend(InputWidgetView, superClass);

  function InputWidgetView() {
    return InputWidgetView.__super__.constructor.apply(this, arguments);
  }

  InputWidgetView.prototype.render = function() {
    InputWidgetView.__super__.render.call(this);
    return this.$el.find('input').prop("disabled", this.model.disabled);
  };

  InputWidgetView.prototype.change_input = function() {
    var ref;
    return (ref = this.model.callback) != null ? ref.execute(this.model) : void 0;
  };

  return InputWidgetView;

})(WidgetView);

export var InputWidget = (function(superClass) {
  extend(InputWidget, superClass);

  function InputWidget() {
    return InputWidget.__super__.constructor.apply(this, arguments);
  }

  InputWidget.prototype.type = "InputWidget";

  InputWidget.prototype.default_view = InputWidgetView;

  InputWidget.define({
    callback: [p.Instance],
    title: [p.String, '']
  });

  return InputWidget;

})(Widget);
