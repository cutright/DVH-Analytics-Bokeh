var extend1 = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  BokehView
} from "core/bokeh_view";

import {
  Visuals
} from "core/visuals";

import {
  logger
} from "core/logging";

import * as p from "core/properties";

import * as proj from "core/util/projections";

import {
  extend
} from "core/util/object";

import {
  Model
} from "../../model";

export var RendererView = (function(superClass) {
  extend1(RendererView, superClass);

  function RendererView() {
    return RendererView.__super__.constructor.apply(this, arguments);
  }

  RendererView.prototype.initialize = function(options) {
    RendererView.__super__.initialize.call(this, options);
    this.plot_view = options.plot_view;
    return this.visuals = new Visuals(this.model);
  };

  RendererView.getters({
    plot_model: function() {
      return this.plot_view.model;
    }
  });

  RendererView.prototype.request_render = function() {
    return this.plot_view.request_render();
  };

  RendererView.prototype.set_data = function(source) {
    var data, ref, ref1;
    data = this.model.materialize_dataspecs(source);
    extend(this, data);
    if (this.plot_model.use_map) {
      if (this._x != null) {
        ref = proj.project_xy(this._x, this._y), this._x = ref[0], this._y = ref[1];
      }
      if (this._xs != null) {
        return ref1 = proj.project_xsys(this._xs, this._ys), this._xs = ref1[0], this._ys = ref1[1], ref1;
      }
    }
  };

  RendererView.prototype.map_to_screen = function(x, y) {
    return this.plot_view.map_to_screen(x, y, this.model.x_range_name, this.model.y_range_name);
  };

  return RendererView;

})(BokehView);

export var Renderer = (function(superClass) {
  extend1(Renderer, superClass);

  function Renderer() {
    return Renderer.__super__.constructor.apply(this, arguments);
  }

  Renderer.prototype.type = "Renderer";

  Renderer.define({
    level: [p.RenderLevel, null],
    visible: [p.Bool, true]
  });

  return Renderer;

})(Model);
