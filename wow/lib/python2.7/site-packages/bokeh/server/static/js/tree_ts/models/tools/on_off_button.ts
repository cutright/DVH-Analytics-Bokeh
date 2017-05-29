var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  ButtonToolButtonView
} from "./button_tool";

export var OnOffButtonView = (function(superClass) {
  extend(OnOffButtonView, superClass);

  function OnOffButtonView() {
    return OnOffButtonView.__super__.constructor.apply(this, arguments);
  }

  OnOffButtonView.prototype.render = function() {
    OnOffButtonView.__super__.render.call(this);
    if (this.model.active) {
      return this.el.classList.add('bk-active');
    } else {
      return this.el.classList.remove('bk-active');
    }
  };

  OnOffButtonView.prototype._clicked = function() {
    var active;
    active = this.model.active;
    return this.model.active = !active;
  };

  return OnOffButtonView;

})(ButtonToolButtonView);
