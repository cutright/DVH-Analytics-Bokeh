"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var column_data_source_1 = require("./column_data_source");
var p = require("core/properties");
exports.RemoteDataSource = (function (superClass) {
    extend(RemoteDataSource, superClass);
    function RemoteDataSource() {
        return RemoteDataSource.__super__.constructor.apply(this, arguments);
    }
    RemoteDataSource.prototype.type = 'RemoteDataSource';
    RemoteDataSource.define({
        data_url: [p.String],
        polling_interval: [p.Number]
    });
    return RemoteDataSource;
})(column_data_source_1.ColumnDataSource);
