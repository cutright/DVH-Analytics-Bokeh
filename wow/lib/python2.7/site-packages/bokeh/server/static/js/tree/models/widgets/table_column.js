"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var cell_formatters_1 = require("./cell_formatters");
var cell_editors_1 = require("./cell_editors");
var p = require("core/properties");
var string_1 = require("core/util/string");
var model_1 = require("../../model");
exports.TableColumn = (function (superClass) {
    extend(TableColumn, superClass);
    function TableColumn() {
        return TableColumn.__super__.constructor.apply(this, arguments);
    }
    TableColumn.prototype.type = 'TableColumn';
    TableColumn.prototype.default_view = null;
    TableColumn.define({
        field: [p.String],
        title: [p.String],
        width: [p.Number, 300],
        formatter: [
            p.Instance, function () {
                return new cell_formatters_1.StringFormatter();
            }
        ],
        editor: [
            p.Instance, function () {
                return new cell_editors_1.StringEditor();
            }
        ],
        sortable: [p.Bool, true],
        default_sort: [p.String, "ascending"]
    });
    TableColumn.prototype.toColumn = function () {
        var ref;
        return {
            id: string_1.uniqueId(),
            field: this.field,
            name: this.title,
            width: this.width,
            formatter: (ref = this.formatter) != null ? ref.doFormat.bind(this.formatter) : void 0,
            editor: this.editor,
            sortable: this.sortable,
            defaultSortAsc: this.default_sort === "ascending"
        };
    };
    return TableColumn;
})(model_1.Model);
