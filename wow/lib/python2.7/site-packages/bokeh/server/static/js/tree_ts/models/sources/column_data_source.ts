var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  ColumnarDataSource
} from "./columnar_data_source";

import {
  HasProps
} from "core/has_props";

import {
  logger
} from "core/logging";

import * as p from "core/properties";

import * as serialization from "core/util/serialization";

import {
  isObject
} from "core/util/types";

export var concat_typed_arrays = function(a, b) {
  var c;
  c = new a.constructor(a.length + b.length);
  c.set(a, 0);
  c.set(b, a.length);
  return c;
};

export var stream_to_column = function(col, new_col, rollover) {
  var end, i, j, l, ref, ref1, ref2, start, tmp, total_len;
  if (col.concat != null) {
    col = col.concat(new_col);
    if (col.length > rollover) {
      col = col.slice(-rollover);
    }
    return col;
  }
  total_len = col.length + new_col.length;
  if ((rollover != null) && total_len > rollover) {
    start = total_len - rollover;
    end = col.length;
    if (col.length < rollover) {
      tmp = new col.constructor(rollover);
      tmp.set(col, 0);
      col = tmp;
    }
    for (i = j = ref = start, ref1 = end; ref <= ref1 ? j < ref1 : j > ref1; i = ref <= ref1 ? ++j : --j) {
      col[i - start] = col[i];
    }
    for (i = l = 0, ref2 = new_col.length; 0 <= ref2 ? l < ref2 : l > ref2; i = 0 <= ref2 ? ++l : --l) {
      col[i + (end - start)] = new_col[i];
    }
    return col;
  }
  tmp = new col.constructor(new_col);
  return concat_typed_arrays(col, tmp);
};

export var patch_to_column = function(col, patch) {
  var i, ind, j, ref, ref1, results, value;
  results = [];
  for (i = j = 0, ref = patch.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
    ref1 = patch[i], ind = ref1[0], value = ref1[1];
    results.push(col[ind] = value);
  }
  return results;
};

export var ColumnDataSource = (function(superClass) {
  extend(ColumnDataSource, superClass);

  function ColumnDataSource() {
    return ColumnDataSource.__super__.constructor.apply(this, arguments);
  }

  ColumnDataSource.prototype.type = 'ColumnDataSource';

  ColumnDataSource.prototype.initialize = function(options) {
    var ref;
    ColumnDataSource.__super__.initialize.call(this, options);
    return ref = serialization.decode_column_data(this.data), this.data = ref[0], this._shapes = ref[1], ref;
  };

  ColumnDataSource.define({
    data: [p.Any, {}]
  });

  ColumnDataSource.prototype.attributes_as_json = function(include_defaults, value_to_json) {
    var attrs, key, ref, value;
    if (include_defaults == null) {
      include_defaults = true;
    }
    if (value_to_json == null) {
      value_to_json = ColumnDataSource._value_to_json;
    }
    attrs = {};
    ref = this.serializable_attributes();
    for (key in ref) {
      if (!hasProp.call(ref, key)) continue;
      value = ref[key];
      if (key === 'data') {
        value = serialization.encode_column_data(value, this._shapes);
      }
      if (include_defaults) {
        attrs[key] = value;
      } else if (key in this._set_after_defaults) {
        attrs[key] = value;
      }
    }
    return value_to_json("attributes", attrs, this);
  };

  ColumnDataSource._value_to_json = function(key, value, optional_parent_object) {
    if (isObject(value) && key === 'data') {
      return serialization.encode_column_data(value, optional_parent_object._shapes);
    } else {
      return HasProps._value_to_json(key, value, optional_parent_object);
    }
  };

  ColumnDataSource.prototype.stream = function(new_data, rollover) {
    var data, k, v;
    data = this.data;
    for (k in new_data) {
      v = new_data[k];
      data[k] = stream_to_column(data[k], new_data[k], rollover);
    }
    this.setv('data', data, {
      silent: true
    });
    return this.trigger('stream');
  };

  ColumnDataSource.prototype.patch = function(patches) {
    var data, k, patch;
    data = this.data;
    for (k in patches) {
      patch = patches[k];
      patch_to_column(data[k], patch);
    }
    this.setv('data', data, {
      silent: true
    });
    return this.trigger('patch');
  };

  return ColumnDataSource;

})(ColumnarDataSource);
