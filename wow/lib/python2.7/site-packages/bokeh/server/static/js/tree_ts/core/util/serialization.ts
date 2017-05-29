var ARRAY_TYPES, DTYPES, _arrayBufferToBase64, _base64ToArrayBuffer, k, v;

import {
  isArray,
  isObject
} from "./types";

ARRAY_TYPES = {
  float32: Float32Array,
  float64: Float64Array,
  uint8: Uint8Array,
  int8: Int8Array,
  uint16: Uint16Array,
  int16: Int16Array,
  uint32: Uint32Array,
  int32: Int32Array
};

DTYPES = {};

for (k in ARRAY_TYPES) {
  v = ARRAY_TYPES[k];
  DTYPES[v.name] = k;
}

_arrayBufferToBase64 = function(buffer) {
  var b, binary, bytes;
  bytes = new Uint8Array(buffer);
  binary = (function() {
    var j, len1, results;
    results = [];
    for (j = 0, len1 = bytes.length; j < len1; j++) {
      b = bytes[j];
      results.push(String.fromCharCode(b));
    }
    return results;
  })();
  return btoa(binary.join(""));
};

_base64ToArrayBuffer = function(base64) {
  var binary_string, bytes, i, j, len, ref;
  binary_string = atob(base64);
  len = binary_string.length;
  bytes = new Uint8Array(len);
  for (i = j = 0, ref = len; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
    bytes[i] = binary_string.charCodeAt(i);
  }
  return bytes.buffer;
};

export var decode_base64 = function(input) {
  var array, bytes, dtype, shape;
  bytes = _base64ToArrayBuffer(input['__ndarray__']);
  dtype = input['dtype'];
  if (dtype in ARRAY_TYPES) {
    array = new ARRAY_TYPES[dtype](bytes);
  }
  shape = input['shape'];
  return [array, shape];
};

export var encode_base64 = function(array, shape) {
  var b64, data, dtype;
  b64 = _arrayBufferToBase64(array.buffer);
  dtype = DTYPES[array.constructor.name];
  data = {
    __ndarray__: b64,
    shape: shape,
    dtype: dtype
  };
  return data;
};

export var decode_column_data = function(data) {
  var arr, arrays, data_shapes, j, len1, new_data, ref, ref1, shape, shapes;
  new_data = {};
  data_shapes = {};
  for (k in data) {
    v = data[k];
    if (isArray(v)) {
      arrays = [];
      shapes = [];
      for (j = 0, len1 = v.length; j < len1; j++) {
        arr = v[j];
        if (isObject(arr) && '__ndarray__' in arr) {
          ref = decode_base64(arr), arr = ref[0], shape = ref[1];
          shapes.push(shape);
          arrays.push(arr);
        } else if (isArray(arr)) {
          shapes.push([]);
          arrays.push(arr);
        }
      }
      if (shapes.length > 0) {
        new_data[k] = arrays;
        data_shapes[k] = shapes;
      } else {
        new_data[k] = v;
      }
    } else if (isObject(v) && '__ndarray__' in v) {
      ref1 = decode_base64(v), arr = ref1[0], shape = ref1[1];
      new_data[k] = arr;
      data_shapes[k] = shape;
    } else {
      new_data[k] = v;
      data_shapes[k] = [];
    }
  }
  return [new_data, data_shapes];
};

export var encode_column_data = function(data, shapes) {
  var i, j, new_array, new_data, ref, ref1, ref2;
  new_data = {};
  for (k in data) {
    v = data[k];
    if ((v != null ? v.buffer : void 0) instanceof ArrayBuffer) {
      v = encode_base64(v, shapes != null ? shapes[k] : void 0);
    } else if (isArray(v)) {
      new_array = [];
      for (i = j = 0, ref = v.length; 0 <= ref ? j < ref : j > ref; i = 0 <= ref ? ++j : --j) {
        if (((ref1 = v[i]) != null ? ref1.buffer : void 0) instanceof ArrayBuffer) {
          new_array.push(encode_base64(v[i], shapes != null ? (ref2 = shapes[k]) != null ? ref2[i] : void 0 : void 0));
        } else {
          new_array.push(v[i]);
        }
      }
      v = new_array;
    }
    new_data[k] = v;
  }
  return new_data;
};
