var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import "jquery-ui/autocomplete";

import {
  TextInput,
  TextInputView
} from "./text_input";

import * as p from "core/properties";

export var AutocompleteInputView = (function(superClass) {
  extend(AutocompleteInputView, superClass);

  function AutocompleteInputView() {
    return AutocompleteInputView.__super__.constructor.apply(this, arguments);
  }

  AutocompleteInputView.prototype.render = function() {
    var $input;
    AutocompleteInputView.__super__.render.call(this);
    $input = this.$el.find("input");
    $input.autocomplete({
      source: this.model.completions
    });
    $input.autocomplete("widget").addClass("bk-autocomplete-input");
    this._prefix_ui();
    return this;
  };

  return AutocompleteInputView;

})(TextInputView);

export var AutocompleteInput = (function(superClass) {
  extend(AutocompleteInput, superClass);

  function AutocompleteInput() {
    return AutocompleteInput.__super__.constructor.apply(this, arguments);
  }

  AutocompleteInput.prototype.type = "AutocompleteInput";

  AutocompleteInput.prototype.default_view = AutocompleteInputView;

  AutocompleteInput.define({
    completions: [p.Array, []]
  });

  return AutocompleteInput;

})(TextInput);
