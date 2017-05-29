var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import * as Backbone from "./backbone";

import {
  uniqueId
} from "./util/string";

export var BokehView = (function(superClass) {
  extend(BokehView, superClass);

  function BokehView() {
    return BokehView.__super__.constructor.apply(this, arguments);
  }

  BokehView.prototype.initialize = function(options) {
    if (options.id == null) {
      return this.id = uniqueId('BokehView');
    }
  };

  BokehView.prototype.toString = function() {
    return this.model.type + "View(" + this.id + ")";
  };

  BokehView.prototype.bind_bokeh_events = function() {};

  BokehView.prototype.remove = function() {
    this.trigger('remove', this);
    return BokehView.__super__.remove.call(this);
  };

  return BokehView;

})(Backbone.View);
