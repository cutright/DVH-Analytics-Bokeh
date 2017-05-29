import {
  HasProps
} from "../has_props";

import {
  isArray,
  isObject
} from "./types";

export var create_ref = function(obj) {
  var ref;
  if (!(obj instanceof HasProps)) {
    throw new Error("can only create refs for HasProps subclasses");
  }
  ref = {
    'type': obj.type,
    'id': obj.id
  };
  if (obj._subtype != null) {
    ref['subtype'] = obj._subtype;
  }
  return ref;
};

export var is_ref = function(arg) {
  var keys;
  if (isObject(arg)) {
    keys = Object.keys(arg).sort();
    if (keys.length === 2) {
      return keys[0] === 'id' && keys[1] === 'type';
    }
    if (keys.length === 3) {
      return keys[0] === 'id' && keys[1] === 'subtype' && keys[2] === 'type';
    }
  }
  return false;
};

export var convert_to_ref = function(value) {
  if (isArray(value)) {
    return value.map(convert_to_ref);
  } else {
    if (value instanceof HasProps) {
      return value.ref();
    }
  }
};
