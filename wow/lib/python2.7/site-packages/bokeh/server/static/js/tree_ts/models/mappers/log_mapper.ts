var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  Model
} from "../../model";

import * as p from "core/properties";

export var LogMapper = (function(superClass) {
  extend(LogMapper, superClass);

  function LogMapper() {
    return LogMapper.__super__.constructor.apply(this, arguments);
  }

  LogMapper.prototype.initialize = function(attrs, options) {
    LogMapper.__super__.initialize.call(this, attrs, options);
    this.define_computed_property('mapper_state', this._mapper_state, true);
    this.add_dependencies('mapper_state', this, ['source_range', 'target_range']);
    this.add_dependencies('mapper_state', this.source_range, ['start', 'end']);
    return this.add_dependencies('mapper_state', this.target_range, ['start', 'end']);
  };

  LogMapper.getters({
    mapper_state: function() {
      return this._get_computed('mapper_state');
    }
  });

  LogMapper.prototype.map_to_target = function(x) {
    var inter_offset, inter_scale, offset, ref, scale, value;
    ref = this.mapper_state, scale = ref[0], offset = ref[1], inter_scale = ref[2], inter_offset = ref[3];
    if (inter_scale === 0) {
      value = 0;
    } else {
      value = (Math.log(x) - inter_offset) / inter_scale;
      if (isNaN(value) || !isFinite(value)) {
        value = 0;
      }
    }
    return value * scale + offset;
  };

  LogMapper.prototype.v_map_to_target = function(xs) {
    var i, inter_offset, inter_scale, j, k, l, offset, ref, ref1, ref2, ref3, result, scale, value;
    ref = this.mapper_state, scale = ref[0], offset = ref[1], inter_scale = ref[2], inter_offset = ref[3];
    result = new Float64Array(xs.length);
    if (inter_scale === 0) {
      for (i = j = 0, ref1 = xs.length; 0 <= ref1 ? j < ref1 : j > ref1; i = 0 <= ref1 ? ++j : --j) {
        result[i] = 0;
      }
    } else {
      for (i = k = 0, ref2 = xs.length; 0 <= ref2 ? k < ref2 : k > ref2; i = 0 <= ref2 ? ++k : --k) {
        value = (Math.log(xs[i]) - inter_offset) / inter_scale;
        if (isNaN(value) || !isFinite(value)) {
          result[i] = 0;
        } else {
          result[i] = value;
        }
      }
    }
    for (i = l = 0, ref3 = xs.length; 0 <= ref3 ? l < ref3 : l > ref3; i = 0 <= ref3 ? ++l : --l) {
      result[i] = result[i] * scale + offset;
    }
    return result;
  };

  LogMapper.prototype.map_from_target = function(xprime) {
    var inter_offset, inter_scale, offset, ref, scale, value;
    ref = this.mapper_state, scale = ref[0], offset = ref[1], inter_scale = ref[2], inter_offset = ref[3];
    value = (xprime - offset) / scale;
    return Math.exp(inter_scale * value + inter_offset);
  };

  LogMapper.prototype.v_map_from_target = function(xprimes) {
    var i, inter_offset, inter_scale, j, offset, ref, ref1, result, scale, value;
    ref = this.mapper_state, scale = ref[0], offset = ref[1], inter_scale = ref[2], inter_offset = ref[3];
    result = new Float64Array(xprimes.length);
    for (i = j = 0, ref1 = xprimes.length; 0 <= ref1 ? j < ref1 : j > ref1; i = 0 <= ref1 ? ++j : --j) {
      value = (xprimes[i] - offset) / scale;
      result[i] = Math.exp(inter_scale * value + inter_offset);
    }
    return result;
  };

  LogMapper.prototype._get_safe_scale = function(orig_start, orig_end) {
    var end, log_val, ref, start;
    if (orig_start < 0) {
      start = 0;
    } else {
      start = orig_start;
    }
    if (orig_end < 0) {
      end = 0;
    } else {
      end = orig_end;
    }
    if (start === end) {
      if (start === 0) {
        ref = [1, 10], start = ref[0], end = ref[1];
      } else {
        log_val = Math.log(start) / Math.log(10);
        start = Math.pow(10, Math.floor(log_val));
        if (Math.ceil(log_val) !== Math.floor(log_val)) {
          end = Math.pow(10, Math.ceil(log_val));
        } else {
          end = Math.pow(10, Math.ceil(log_val) + 1);
        }
      }
    }
    return [start, end];
  };

  LogMapper.prototype._mapper_state = function() {
    var end, inter_offset, inter_scale, offset, ref, scale, screen_range, source_end, source_start, start, target_end, target_start;
    source_start = this.source_range.start;
    source_end = this.source_range.end;
    target_start = this.target_range.start;
    target_end = this.target_range.end;
    screen_range = target_end - target_start;
    ref = this._get_safe_scale(source_start, source_end), start = ref[0], end = ref[1];
    if (start === 0) {
      inter_scale = Math.log(end);
      inter_offset = 0;
    } else {
      inter_scale = Math.log(end) - Math.log(start);
      inter_offset = Math.log(start);
    }
    scale = screen_range;
    offset = target_start;
    return [scale, offset, inter_scale, inter_offset];
  };

  LogMapper.internal({
    source_range: [p.Any],
    target_range: [p.Any]
  });

  return LogMapper;

})(Model);
