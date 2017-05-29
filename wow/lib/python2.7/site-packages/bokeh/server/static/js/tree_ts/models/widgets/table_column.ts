var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  StringFormatter
} from "./cell_formatters";

import {
  StringEditor
} from "./cell_editors";

import * as p from "core/properties";

import {
  uniqueId
} from "core/util/string";

import {
  Model
} from "../../model";

export var TableColumn = (function(superClass) {
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
      p.Instance, function() {
        return new StringFormatter();
      }
    ],
    editor: [
      p.Instance, function() {
        return new StringEditor();
      }
    ],
    sortable: [p.Bool, true],
    default_sort: [p.String, "ascending"]
  });

  TableColumn.prototype.toColumn = function() {
    var ref;
    return {
      id: uniqueId(),
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

})(Model);
