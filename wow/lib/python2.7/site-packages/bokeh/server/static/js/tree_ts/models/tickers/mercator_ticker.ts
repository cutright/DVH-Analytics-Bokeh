var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  BasicTicker
} from "./basic_ticker";

import * as p from "core/properties";

import {
  proj4,
  mercator
} from "core/util/proj4";

export var MercatorTicker = (function(superClass) {
  extend(MercatorTicker, superClass);

  function MercatorTicker() {
    return MercatorTicker.__super__.constructor.apply(this, arguments);
  }

  MercatorTicker.prototype.type = 'MercatorTicker';

  MercatorTicker.define({
    dimension: [p.LatLon]
  });

  MercatorTicker.prototype.get_ticks_no_defaults = function(data_low, data_high, cross_loc, desired_n_ticks) {
    var _, i, j, k, l, lat, len, len1, len2, len3, lon, proj_cross_loc, proj_high, proj_low, proj_ticks, ref, ref1, ref10, ref11, ref2, ref3, ref4, ref5, ref6, ref7, ref8, ref9, tick, ticks;
    if (this.dimension == null) {
      throw new Error("MercatorTicker.dimension not configured");
    }
    if (this.dimension === "lon") {
      ref = proj4(mercator).inverse([data_low, cross_loc]), proj_low = ref[0], proj_cross_loc = ref[1];
      ref1 = proj4(mercator).inverse([data_high, cross_loc]), proj_high = ref1[0], proj_cross_loc = ref1[1];
    } else {
      ref2 = proj4(mercator).inverse([cross_loc, data_low]), proj_cross_loc = ref2[0], proj_low = ref2[1];
      ref3 = proj4(mercator).inverse([cross_loc, data_high]), proj_cross_loc = ref3[0], proj_high = ref3[1];
    }
    proj_ticks = MercatorTicker.__super__.get_ticks_no_defaults.call(this, proj_low, proj_high, cross_loc, desired_n_ticks);
    ticks = {
      major: [],
      minor: []
    };
    if (this.dimension === "lon") {
      ref4 = proj_ticks.major;
      for (i = 0, len = ref4.length; i < len; i++) {
        tick = ref4[i];
        ref5 = proj4(mercator).forward([tick, proj_cross_loc]), lon = ref5[0], _ = ref5[1];
        ticks.major.push(lon);
      }
      ref6 = proj_ticks.minor;
      for (j = 0, len1 = ref6.length; j < len1; j++) {
        tick = ref6[j];
        ref7 = proj4(mercator).forward([tick, proj_cross_loc]), lon = ref7[0], _ = ref7[1];
        ticks.minor.push(lon);
      }
    } else {
      ref8 = proj_ticks.major;
      for (k = 0, len2 = ref8.length; k < len2; k++) {
        tick = ref8[k];
        ref9 = proj4(mercator).forward([proj_cross_loc, tick]), _ = ref9[0], lat = ref9[1];
        ticks.major.push(lat);
      }
      ref10 = proj_ticks.minor;
      for (l = 0, len3 = ref10.length; l < len3; l++) {
        tick = ref10[l];
        ref11 = proj4(mercator).forward([proj_cross_loc, tick]), _ = ref11[0], lat = ref11[1];
        ticks.minor.push(lat);
      }
    }
    return ticks;
  };

  return MercatorTicker;

})(BasicTicker);
