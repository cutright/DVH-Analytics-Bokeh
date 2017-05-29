var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  logger
} from "core/logging";

import {
  GMapPlotCanvas
} from "./gmap_plot_canvas";

import {
  Plot,
  PlotView
} from "./plot";

import * as p from "core/properties";

import {
  Model
} from "../../model";

export var MapOptions = (function(superClass) {
  extend(MapOptions, superClass);

  function MapOptions() {
    return MapOptions.__super__.constructor.apply(this, arguments);
  }

  MapOptions.prototype.type = 'MapOptions';

  MapOptions.define({
    lat: [p.Number],
    lng: [p.Number],
    zoom: [p.Number, 12]
  });

  return MapOptions;

})(Model);

export var GMapOptions = (function(superClass) {
  extend(GMapOptions, superClass);

  function GMapOptions() {
    return GMapOptions.__super__.constructor.apply(this, arguments);
  }

  GMapOptions.prototype.type = 'GMapOptions';

  GMapOptions.define({
    map_type: [p.String, "roadmap"],
    scale_control: [p.Bool, false],
    styles: [p.String]
  });

  return GMapOptions;

})(MapOptions);

export var GMapPlotView = (function(superClass) {
  extend(GMapPlotView, superClass);

  function GMapPlotView() {
    return GMapPlotView.__super__.constructor.apply(this, arguments);
  }

  return GMapPlotView;

})(PlotView);

export var GMapPlot = (function(superClass) {
  extend(GMapPlot, superClass);

  function GMapPlot() {
    return GMapPlot.__super__.constructor.apply(this, arguments);
  }

  GMapPlot.prototype.type = 'GMapPlot';

  GMapPlot.prototype.default_view = GMapPlotView;

  GMapPlot.prototype.initialize = function(options) {
    GMapPlot.__super__.initialize.call(this, options);
    if (!this.api_key) {
      logger.error("api_key is required. See https://developers.google.com/maps/documentation/javascript/get-api-key for more information on how to obtain your own.");
    }
    this._plot_canvas = new GMapPlotCanvas({
      plot: this
    });
    return this.plot_canvas.toolbar = this.toolbar;
  };

  GMapPlot.define({
    map_options: [p.Instance],
    api_key: [p.String]
  });

  return GMapPlot;

})(Plot);
