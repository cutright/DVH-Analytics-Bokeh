var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  DataSource
} from "./data_source";

import {
  logger
} from "core/logging";

import {
  SelectionManager
} from "core/selection_manager";

import * as p from "core/properties";

import {
  uniq
} from "core/util/array";

export var ColumnarDataSource = (function(superClass) {
  extend(ColumnarDataSource, superClass);

  function ColumnarDataSource() {
    return ColumnarDataSource.__super__.constructor.apply(this, arguments);
  }

  ColumnarDataSource.prototype.type = 'ColumnarDataSource';

  ColumnarDataSource.define({
    column_names: [p.Array, []]
  });

  ColumnarDataSource.internal({
    selection_manager: [
      p.Instance, function(self) {
        return new SelectionManager({
          source: self
        });
      }
    ],
    inspected: [p.Any],
    _shapes: [p.Any, {}]
  });

  ColumnarDataSource.prototype.get_column = function(colname) {
    var ref;
    return (ref = this.data[colname]) != null ? ref : null;
  };

  ColumnarDataSource.prototype.columns = function() {
    return Object.keys(this.data);
  };

  ColumnarDataSource.prototype.get_length = function(soft) {
    var _key, lengths, msg, val;
    if (soft == null) {
      soft = true;
    }
    lengths = uniq((function() {
      var ref, results;
      ref = this.data;
      results = [];
      for (_key in ref) {
        val = ref[_key];
        results.push(val.length);
      }
      return results;
    }).call(this));
    switch (lengths.length) {
      case 0:
        return null;
      case 1:
        return lengths[0];
      default:
        msg = "data source has columns of inconsistent lengths";
        if (soft) {
          logger.warn(msg);
          return lengths.sort()[0];
        } else {
          throw new Error(msg);
        }
    }
  };

  return ColumnarDataSource;

})(DataSource);
