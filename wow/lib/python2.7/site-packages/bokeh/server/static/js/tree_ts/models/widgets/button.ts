var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import * as p from "core/properties";

import {
  register_with_event,
  ButtonClick
} from "core/bokeh_events";

import {
  AbstractButton,
  AbstractButtonView
} from "./abstract_button";

export var ButtonView = (function(superClass) {
  extend(ButtonView, superClass);

  function ButtonView() {
    return ButtonView.__super__.constructor.apply(this, arguments);
  }

  ButtonView.prototype.change_input = function() {
    this.model.trigger_event(new ButtonClick({}));
    this.model.clicks = this.model.clicks + 1;
    return ButtonView.__super__.change_input.call(this);
  };

  return ButtonView;

})(AbstractButtonView);

export var Button = (function(superClass) {
  extend(Button, superClass);

  function Button() {
    return Button.__super__.constructor.apply(this, arguments);
  }

  Button.prototype.type = "Button";

  Button.prototype.default_view = ButtonView;

  Button.define({
    clicks: [p.Number, 0]
  });

  return Button;

})(AbstractButton);

register_with_event(ButtonClick, Button);
