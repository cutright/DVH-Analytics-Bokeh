var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  DataRange
} from "./data_range";

import {
  GlyphRenderer
} from "../renderers/glyph_renderer";

import {
  logger
} from "core/logging";

import * as p from "core/properties";

import * as bbox from "core/util/bbox";

export var DataRange1d = (function(superClass) {
  extend(DataRange1d, superClass);

  function DataRange1d() {
    return DataRange1d.__super__.constructor.apply(this, arguments);
  }

  DataRange1d.prototype.type = 'DataRange1d';

  DataRange1d.define({
    start: [p.Number],
    end: [p.Number],
    range_padding: [p.Number, 0.1],
    flipped: [p.Bool, false],
    follow: [p.String],
    follow_interval: [p.Number],
    default_span: [p.Number, 2],
    bounds: [p.Any],
    min_interval: [p.Any],
    max_interval: [p.Any]
  });

  DataRange1d.internal({
    mapper_hint: [p.String, 'auto']
  });

  DataRange1d.prototype.initialize = function(attrs, options) {
    DataRange1d.__super__.initialize.call(this, attrs, options);
    this.plot_bounds = {};
    this.have_updated_interactively = false;
    this._initial_start = this.start;
    this._initial_end = this.end;
    this._initial_range_padding = this.range_padding;
    this._initial_follow = this.follow;
    this._initial_follow_interval = this.follow_interval;
    return this._initial_default_span = this.default_span;
  };

  DataRange1d.getters({
    min: function() {
      return Math.min(this.start, this.end);
    },
    max: function() {
      return Math.max(this.start, this.end);
    }
  });

  DataRange1d.prototype.computed_renderers = function() {
    var all_renderers, i, j, len, len1, names, plot, r, ref, renderers, rs;
    names = this.names;
    renderers = this.renderers;
    if (renderers.length === 0) {
      ref = this.plots;
      for (i = 0, len = ref.length; i < len; i++) {
        plot = ref[i];
        all_renderers = plot.renderers;
        rs = (function() {
          var j, len1, results;
          results = [];
          for (j = 0, len1 = all_renderers.length; j < len1; j++) {
            r = all_renderers[j];
            if (r instanceof GlyphRenderer) {
              results.push(r);
            }
          }
          return results;
        })();
        renderers = renderers.concat(rs);
      }
    }
    if (names.length > 0) {
      renderers = (function() {
        var j, len1, results;
        results = [];
        for (j = 0, len1 = renderers.length; j < len1; j++) {
          r = renderers[j];
          if (names.indexOf(r.name) >= 0) {
            results.push(r);
          }
        }
        return results;
      })();
    }
    logger.debug("computed " + renderers.length + " renderers for DataRange1d " + this.id);
    for (j = 0, len1 = renderers.length; j < len1; j++) {
      r = renderers[j];
      logger.trace(" - " + r.type + " " + r.id);
    }
    return renderers;
  };

  DataRange1d.prototype._compute_plot_bounds = function(renderers, bounds) {
    var i, len, r, result;
    result = bbox.empty();
    for (i = 0, len = renderers.length; i < len; i++) {
      r = renderers[i];
      if (bounds[r.id] != null) {
        result = bbox.union(result, bounds[r.id]);
      }
    }
    return result;
  };

  DataRange1d.prototype._compute_min_max = function(plot_bounds, dimension) {
    var k, max, min, overall, ref, ref1, v;
    overall = bbox.empty();
    for (k in plot_bounds) {
      v = plot_bounds[k];
      overall = bbox.union(overall, v);
    }
    if (dimension === 0) {
      ref = [overall.minX, overall.maxX], min = ref[0], max = ref[1];
    } else {
      ref1 = [overall.minY, overall.maxY], min = ref1[0], max = ref1[1];
    }
    return [min, max];
  };

  DataRange1d.prototype._compute_range = function(min, max) {
    var center, end, follow_interval, follow_sign, log_max, log_min, range_padding, ref, ref1, ref2, ref3, span, start;
    range_padding = this.range_padding;
    if ((range_padding != null) && range_padding > 0) {
      if (this.mapper_hint === "log") {
        if (isNaN(min) || !isFinite(min) || min <= 0) {
          if (isNaN(max) || !isFinite(max) || max <= 0) {
            min = 0.1;
          } else {
            min = max / 100;
          }
          logger.warn("could not determine minimum data value for log axis, DataRange1d using value " + min);
        }
        if (isNaN(max) || !isFinite(max) || max <= 0) {
          if (isNaN(min) || !isFinite(min) || min <= 0) {
            max = 10;
          } else {
            max = min * 100;
          }
          logger.warn("could not determine maximum data value for log axis, DataRange1d using value " + max);
        }
        log_min = Math.log(min) / Math.log(10);
        log_max = Math.log(max) / Math.log(10);
        if (max === min) {
          span = this.default_span + 0.001;
        } else {
          span = (log_max - log_min) * (1 + range_padding);
        }
        center = (log_min + log_max) / 2.0;
        ref = [Math.pow(10, center - span / 2.0), Math.pow(10, center + span / 2.0)], start = ref[0], end = ref[1];
      } else {
        if (max === min) {
          span = this.default_span;
        } else {
          span = (max - min) * (1 + range_padding);
        }
        center = (max + min) / 2.0;
        ref1 = [center - span / 2.0, center + span / 2.0], start = ref1[0], end = ref1[1];
      }
    } else {
      ref2 = [min, max], start = ref2[0], end = ref2[1];
    }
    follow_sign = +1;
    if (this.flipped) {
      ref3 = [end, start], start = ref3[0], end = ref3[1];
      follow_sign = -1;
    }
    follow_interval = this.follow_interval;
    if ((follow_interval != null) && Math.abs(start - end) > follow_interval) {
      if (this.follow === 'start') {
        end = start + follow_sign * follow_interval;
      } else if (this.follow === 'end') {
        start = end - follow_sign * follow_interval;
      }
    }
    return [start, end];
  };

  DataRange1d.prototype.update = function(bounds, dimension, bounds_id) {
    var _end, _start, end, max, min, new_range, ref, ref1, ref2, renderers, start;
    if (this.have_updated_interactively) {
      return;
    }
    renderers = this.computed_renderers();
    this.plot_bounds[bounds_id] = this._compute_plot_bounds(renderers, bounds);
    ref = this._compute_min_max(this.plot_bounds, dimension), min = ref[0], max = ref[1];
    ref1 = this._compute_range(min, max), start = ref1[0], end = ref1[1];
    if (this._initial_start != null) {
      if (this.mapper_hint === "log") {
        if (this._initial_start > 0) {
          start = this._initial_start;
        }
      } else {
        start = this._initial_start;
      }
    }
    if (this._initial_end != null) {
      if (this.mapper_hint === "log") {
        if (this._initial_end > 0) {
          end = this._initial_end;
        }
      } else {
        end = this._initial_end;
      }
    }
    ref2 = [this.start, this.end], _start = ref2[0], _end = ref2[1];
    if (start !== _start || end !== _end) {
      new_range = {};
      if (start !== _start) {
        new_range.start = start;
      }
      if (end !== _end) {
        new_range.end = end;
      }
      this.setv(new_range);
    }
    if (this.bounds === 'auto') {
      this.setv({
        bounds: [start, end]
      }, {
        silent: true
      });
    }
    return this.trigger('change');
  };

  DataRange1d.prototype.reset = function() {
    this.have_updated_interactively = false;
    this.setv({
      range_padding: this._initial_range_padding,
      follow: this._initial_follow,
      follow_interval: this._initial_follow_interval,
      default_span: this._initial_default_span
    }, {
      silent: true
    });
    return this.trigger('change');
  };

  return DataRange1d;

})(DataRange);
