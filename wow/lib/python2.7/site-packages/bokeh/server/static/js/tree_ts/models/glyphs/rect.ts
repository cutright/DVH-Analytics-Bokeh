var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  XYGlyph,
  XYGlyphView
} from "./xy_glyph";

import * as hittest from "core/hittest";

import * as p from "core/properties";

import {
  max
} from "core/util/array";

import {
  isString
} from "core/util/types";

import {
  CategoricalMapper
} from "../mappers/categorical_mapper";

export var RectView = (function(superClass) {
  extend(RectView, superClass);

  function RectView() {
    return RectView.__super__.constructor.apply(this, arguments);
  }

  RectView.prototype._set_data = function() {
    this.max_w2 = 0;
    if (this.model.properties.width.units === "data") {
      this.max_w2 = this.max_width / 2;
    }
    this.max_h2 = 0;
    if (this.model.properties.height.units === "data") {
      return this.max_h2 = this.max_height / 2;
    }
  };

  RectView.prototype._map_data = function() {
    var canvas, i, ref, ref1;
    canvas = this.renderer.plot_view.canvas;
    if (this.model.properties.width.units === "data") {
      ref = this._map_dist_corner_for_data_side_length(this._x, this._width, this.renderer.xmapper, canvas, 0), this.sw = ref[0], this.sx0 = ref[1];
    } else {
      this.sw = this._width;
      this.sx0 = (function() {
        var j, ref1, results;
        results = [];
        for (i = j = 0, ref1 = this.sx.length; 0 <= ref1 ? j < ref1 : j > ref1; i = 0 <= ref1 ? ++j : --j) {
          results.push(this.sx[i] - this.sw[i] / 2);
        }
        return results;
      }).call(this);
    }
    if (this.model.properties.height.units === "data") {
      ref1 = this._map_dist_corner_for_data_side_length(this._y, this._height, this.renderer.ymapper, canvas, 1), this.sh = ref1[0], this.sy1 = ref1[1];
    } else {
      this.sh = this._height;
      this.sy1 = (function() {
        var j, ref2, results;
        results = [];
        for (i = j = 0, ref2 = this.sy.length; 0 <= ref2 ? j < ref2 : j > ref2; i = 0 <= ref2 ? ++j : --j) {
          results.push(this.sy[i] - this.sh[i] / 2);
        }
        return results;
      }).call(this);
    }
    return this.ssemi_diag = (function() {
      var j, ref2, results;
      results = [];
      for (i = j = 0, ref2 = this.sw.length; 0 <= ref2 ? j < ref2 : j > ref2; i = 0 <= ref2 ? ++j : --j) {
        results.push(Math.sqrt(this.sw[i] / 2 * this.sw[i] / 2 + this.sh[i] / 2 * this.sh[i] / 2));
      }
      return results;
    }).call(this);
  };

  RectView.prototype._render = function(ctx, indices, arg) {
    var _angle, i, j, k, len, len1, sh, sw, sx, sx0, sy, sy1;
    sx = arg.sx, sy = arg.sy, sx0 = arg.sx0, sy1 = arg.sy1, sw = arg.sw, sh = arg.sh, _angle = arg._angle;
    if (this.visuals.fill.doit) {
      for (j = 0, len = indices.length; j < len; j++) {
        i = indices[j];
        if (isNaN(sx[i] + sy[i] + sx0[i] + sy1[i] + sw[i] + sh[i] + _angle[i])) {
          continue;
        }
        this.visuals.fill.set_vectorize(ctx, i);
        if (_angle[i]) {
          ctx.translate(sx[i], sy[i]);
          ctx.rotate(_angle[i]);
          ctx.fillRect(-sw[i] / 2, -sh[i] / 2, sw[i], sh[i]);
          ctx.rotate(-_angle[i]);
          ctx.translate(-sx[i], -sy[i]);
        } else {
          ctx.fillRect(sx0[i], sy1[i], sw[i], sh[i]);
        }
      }
    }
    if (this.visuals.line.doit) {
      ctx.beginPath();
      for (k = 0, len1 = indices.length; k < len1; k++) {
        i = indices[k];
        if (isNaN(sx[i] + sy[i] + sx0[i] + sy1[i] + sw[i] + sh[i] + _angle[i])) {
          continue;
        }
        if (sw[i] === 0 || sh[i] === 0) {
          continue;
        }
        if (_angle[i]) {
          ctx.translate(sx[i], sy[i]);
          ctx.rotate(_angle[i]);
          ctx.rect(-sw[i] / 2, -sh[i] / 2, sw[i], sh[i]);
          ctx.rotate(-_angle[i]);
          ctx.translate(-sx[i], -sy[i]);
        } else {
          ctx.rect(sx0[i], sy1[i], sw[i], sh[i]);
        }
        this.visuals.line.set_vectorize(ctx, i);
        ctx.stroke();
        ctx.beginPath();
      }
      return ctx.stroke();
    }
  };

  RectView.prototype._hit_rect = function(geometry) {
    var bbox, ref, ref1, result, x0, x1, y0, y1;
    ref = this.renderer.xmapper.v_map_from_target([geometry.vx0, geometry.vx1], true), x0 = ref[0], x1 = ref[1];
    ref1 = this.renderer.ymapper.v_map_from_target([geometry.vy0, geometry.vy1], true), y0 = ref1[0], y1 = ref1[1];
    bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
    result = hittest.create_hit_test_result();
    result['1d'].indices = this.index.indices(bbox);
    return result;
  };

  RectView.prototype._hit_point = function(geometry) {
    var bbox, c, d, height_in, hits, i, j, len, max_x2_ddist, max_y2_ddist, px, py, ref, ref1, result, s, scenter_x, scenter_y, sx, sy, vx, vy, width_in, x, x0, x1, y, y0, y1;
    ref = [geometry.vx, geometry.vy], vx = ref[0], vy = ref[1];
    x = this.renderer.xmapper.map_from_target(vx, true);
    y = this.renderer.ymapper.map_from_target(vy, true);
    scenter_x = (function() {
      var j, ref1, results;
      results = [];
      for (i = j = 0, ref1 = this.sx0.length; 0 <= ref1 ? j < ref1 : j > ref1; i = 0 <= ref1 ? ++j : --j) {
        results.push(this.sx0[i] + this.sw[i] / 2);
      }
      return results;
    }).call(this);
    scenter_y = (function() {
      var j, ref1, results;
      results = [];
      for (i = j = 0, ref1 = this.sy1.length; 0 <= ref1 ? j < ref1 : j > ref1; i = 0 <= ref1 ? ++j : --j) {
        results.push(this.sy1[i] + this.sh[i] / 2);
      }
      return results;
    }).call(this);
    max_x2_ddist = max(this._ddist(0, scenter_x, this.ssemi_diag));
    max_y2_ddist = max(this._ddist(1, scenter_y, this.ssemi_diag));
    x0 = x - max_x2_ddist;
    x1 = x + max_x2_ddist;
    y0 = y - max_y2_ddist;
    y1 = y + max_y2_ddist;
    hits = [];
    bbox = hittest.validate_bbox_coords([x0, x1], [y0, y1]);
    ref1 = this.index.indices(bbox);
    for (j = 0, len = ref1.length; j < len; j++) {
      i = ref1[j];
      sx = this.renderer.plot_view.canvas.vx_to_sx(vx);
      sy = this.renderer.plot_view.canvas.vy_to_sy(vy);
      if (this._angle[i]) {
        d = Math.sqrt(Math.pow(sx - this.sx[i], 2) + Math.pow(sy - this.sy[i], 2));
        s = Math.sin(-this._angle[i]);
        c = Math.cos(-this._angle[i]);
        px = c * (sx - this.sx[i]) - s * (sy - this.sy[i]) + this.sx[i];
        py = s * (sx - this.sx[i]) + c * (sy - this.sy[i]) + this.sy[i];
        sx = px;
        sy = py;
        width_in = Math.abs(this.sx[i] - sx) <= this.sw[i] / 2;
        height_in = Math.abs(this.sy[i] - sy) <= this.sh[i] / 2;
      } else {
        width_in = sx - this.sx0[i] <= this.sw[i] && sx - this.sx0[i] >= 0;
        height_in = sy - this.sy1[i] <= this.sh[i] && sy - this.sy1[i] >= 0;
      }
      if (height_in && width_in) {
        hits.push(i);
      }
    }
    result = hittest.create_hit_test_result();
    result['1d'].indices = hits;
    return result;
  };

  RectView.prototype._map_dist_corner_for_data_side_length = function(coord, side_length, mapper, canvas, dim) {
    var i, pt0, pt1, return_synthetic, sside_length, synthetic_pt, synthetic_pt_corner, vpt0, vpt1, vpt_corner;
    if (isString(coord[0]) && mapper instanceof CategoricalMapper) {
      return_synthetic = true;
      synthetic_pt = mapper.v_map_to_target(coord, return_synthetic);
      if (dim === 0) {
        synthetic_pt_corner = (function() {
          var j, ref, results;
          results = [];
          for (i = j = 0, ref = coord.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
            results.push(synthetic_pt[i] - side_length[i] / 2);
          }
          return results;
        })();
      } else if (dim === 1) {
        synthetic_pt_corner = (function() {
          var j, ref, results;
          results = [];
          for (i = j = 0, ref = coord.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
            results.push(synthetic_pt[i] + side_length[i] / 2);
          }
          return results;
        })();
      }
      vpt_corner = mapper.v_map_to_target(synthetic_pt_corner);
      sside_length = this.sdist(mapper, coord, side_length, 'center', this.model.dilate);
    } else {
      pt0 = (function() {
        var j, ref, results;
        results = [];
        for (i = j = 0, ref = coord.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
          results.push(Number(coord[i]) - side_length[i] / 2);
        }
        return results;
      })();
      pt1 = (function() {
        var j, ref, results;
        results = [];
        for (i = j = 0, ref = coord.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
          results.push(Number(coord[i]) + side_length[i] / 2);
        }
        return results;
      })();
      vpt0 = mapper.v_map_to_target(pt0);
      vpt1 = mapper.v_map_to_target(pt1);
      sside_length = this.sdist(mapper, pt0, side_length, 'edge', this.model.dilate);
      if (dim === 0) {
        vpt_corner = vpt0[0] < vpt1[0] ? vpt0 : vpt1;
      } else if (dim === 1) {
        vpt_corner = vpt0[0] < vpt1[0] ? vpt1 : vpt0;
      }
    }
    if (dim === 0) {
      return [sside_length, canvas.v_vx_to_sx(vpt_corner)];
    } else if (dim === 1) {
      return [sside_length, canvas.v_vy_to_sy(vpt_corner)];
    }
  };

  RectView.prototype._ddist = function(dim, spts, spans) {
    var i, mapper, pt0, pt1, vpt0, vpt1, vpts;
    if (dim === 0) {
      vpts = this.renderer.plot_view.canvas.v_sx_to_vx(spts);
      mapper = this.renderer.xmapper;
    } else {
      vpts = this.renderer.plot_view.canvas.v_vy_to_sy(spts);
      mapper = this.renderer.ymapper;
    }
    vpt0 = vpts;
    vpt1 = (function() {
      var j, ref, results;
      results = [];
      for (i = j = 0, ref = vpt0.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
        results.push(vpt0[i] + spans[i]);
      }
      return results;
    })();
    pt0 = mapper.v_map_from_target(vpt0);
    pt1 = mapper.v_map_from_target(vpt1);
    return (function() {
      var j, ref, results;
      results = [];
      for (i = j = 0, ref = pt0.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
        results.push(Math.abs(pt1[i] - pt0[i]));
      }
      return results;
    })();
  };

  RectView.prototype.draw_legend_for_index = function(ctx, x0, x1, y0, y1, index) {
    return this._generic_area_legend(ctx, x0, x1, y0, y1, index);
  };

  RectView.prototype._bounds = function(bds) {
    return this.max_wh2_bounds(bds);
  };

  return RectView;

})(XYGlyphView);

export var Rect = (function(superClass) {
  extend(Rect, superClass);

  function Rect() {
    return Rect.__super__.constructor.apply(this, arguments);
  }

  Rect.prototype.default_view = RectView;

  Rect.prototype.type = 'Rect';

  Rect.mixins(['line', 'fill']);

  Rect.define({
    angle: [p.AngleSpec, 0],
    width: [p.DistanceSpec],
    height: [p.DistanceSpec],
    dilate: [p.Bool, false]
  });

  return Rect;

})(XYGlyph);
