var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import * as p from "core/properties";

import {
  Widget,
  WidgetView
} from "./widget";

import template from "./markup_template";

export var MarkupView = (function(superClass) {
  extend(MarkupView, superClass);

  function MarkupView() {
    return MarkupView.__super__.constructor.apply(this, arguments);
  }

  MarkupView.prototype.template = template;

  MarkupView.prototype.initialize = function(options) {
    MarkupView.__super__.initialize.call(this, options);
    this.render();
    return this.listenTo(this.model, 'change', this.render);
  };

  MarkupView.prototype.render = function() {
    MarkupView.__super__.render.call(this);
    this.$el.empty();
    this.$el.html(this.template());
    if (this.model.height) {
      this.$el.height(this.model.height);
    }
    if (this.model.width) {
      return this.$el.width(this.model.width);
    }
  };

  return MarkupView;

})(WidgetView);

export var Markup = (function(superClass) {
  extend(Markup, superClass);

  function Markup() {
    return Markup.__super__.constructor.apply(this, arguments);
  }

  Markup.prototype.type = "Markup";

  Markup.prototype.initialize = function(options) {
    return Markup.__super__.initialize.call(this, options);
  };

  Markup.define({
    text: [p.String, '']
  });

  return Markup;

})(Widget);
