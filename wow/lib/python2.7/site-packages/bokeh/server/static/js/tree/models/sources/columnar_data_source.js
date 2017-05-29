"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var data_source_1 = require("./data_source");
var logging_1 = require("core/logging");
var selection_manager_1 = require("core/selection_manager");
var p = require("core/properties");
var array_1 = require("core/util/array");
exports.ColumnarDataSource = (function (superClass) {
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
            p.Instance, function (self) {
                return new selection_manager_1.SelectionManager({
                    source: self
                });
            }
        ],
        inspected: [p.Any],
        _shapes: [p.Any, {}]
    });
    ColumnarDataSource.prototype.get_column = function (colname) {
        var ref;
        return (ref = this.data[colname]) != null ? ref : null;
    };
    ColumnarDataSource.prototype.columns = function () {
        return Object.keys(this.data);
    };
    ColumnarDataSource.prototype.get_length = function (soft) {
        var _key, lengths, msg, val;
        if (soft == null) {
            soft = true;
        }
        lengths = array_1.uniq((function () {
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
                    logging_1.logger.warn(msg);
                    return lengths.sort()[0];
                }
                else {
                    throw new Error(msg);
                }
        }
    };
    return ColumnarDataSource;
})(data_source_1.DataSource);
