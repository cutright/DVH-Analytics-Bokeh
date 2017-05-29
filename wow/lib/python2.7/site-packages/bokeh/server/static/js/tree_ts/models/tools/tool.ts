var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  logger
} from "core/logging";

import * as p from "core/properties";

import {
  BokehView
} from "core/bokeh_view";

import {
  min,
  max
} from "core/util/array";

import {
  Model
} from "../../model";

export var ToolView = (function(superClass) {
  extend(ToolView, superClass);

  function ToolView() {
    return ToolView.__super__.constructor.apply(this, arguments);
  }

  ToolView.prototype.initialize = function(options) {
    ToolView.__super__.initialize.call(this, options);
    return this.plot_view = options.plot_view;
  };

  ToolView.getters({
    plot_model: function() {
      return this.plot_view.model;
    }
  });

  ToolView.prototype.bind_bokeh_events = function() {
    return this.listenTo(this.model, 'change:active', (function(_this) {
      return function() {
        if (_this.model.active) {
          return _this.activate();
        } else {
          return _this.deactivate();
        }
      };
    })(this));
  };

  ToolView.prototype.activate = function() {};

  ToolView.prototype.deactivate = function() {};

  return ToolView;

})(BokehView);

export var Tool = (function(superClass) {
  extend(Tool, superClass);

  function Tool() {
    return Tool.__super__.constructor.apply(this, arguments);
  }

  Tool.getters({
    synthetic_renderers: function() {
      return [];
    }
  });

  Tool.define({
    plot: [p.Instance]
  });

  Tool.internal({
    active: [p.Boolean, false]
  });

  Tool.prototype._get_dim_tooltip = function(name, dims) {
    switch (dims) {
      case 'width':
        return name + " (x-axis)";
      case 'height':
        return name + " (y-axis)";
      case 'both':
        return name;
    }
  };

  Tool.prototype._get_dim_limits = function(arg, arg1, frame, dims) {
    var hr, vr, vx0, vx1, vxlim, vy0, vy1, vylim;
    vx0 = arg[0], vy0 = arg[1];
    vx1 = arg1[0], vy1 = arg1[1];
    hr = frame.h_range;
    if (dims === 'width' || dims === 'both') {
      vxlim = [min([vx0, vx1]), max([vx0, vx1])];
      vxlim = [max([vxlim[0], hr.min]), min([vxlim[1], hr.max])];
    } else {
      vxlim = [hr.min, hr.max];
    }
    vr = frame.v_range;
    if (dims === 'height' || dims === 'both') {
      vylim = [min([vy0, vy1]), max([vy0, vy1])];
      vylim = [max([vylim[0], vr.min]), min([vylim[1], vr.max])];
    } else {
      vylim = [vr.min, vr.max];
    }
    return [vxlim, vylim];
  };

  return Tool;

})(Model);
