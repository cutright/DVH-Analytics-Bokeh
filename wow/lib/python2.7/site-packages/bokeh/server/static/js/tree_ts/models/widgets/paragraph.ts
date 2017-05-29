var extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  Markup,
  MarkupView
} from "./markup";

import {
  p
} from "core/dom";

export var ParagraphView = (function(superClass) {
  extend(ParagraphView, superClass);

  function ParagraphView() {
    return ParagraphView.__super__.constructor.apply(this, arguments);
  }

  ParagraphView.prototype.render = function() {
    var content;
    ParagraphView.__super__.render.call(this);
    content = p({
      style: {
        margin: 0
      }
    }, this.model.text);
    return this.$el.find('.bk-markup').append(content);
  };

  return ParagraphView;

})(MarkupView);

export var Paragraph = (function(superClass) {
  extend(Paragraph, superClass);

  function Paragraph() {
    return Paragraph.__super__.constructor.apply(this, arguments);
  }

  Paragraph.prototype.type = "Paragraph";

  Paragraph.prototype.default_view = ParagraphView;

  return Paragraph;

})(Markup);
