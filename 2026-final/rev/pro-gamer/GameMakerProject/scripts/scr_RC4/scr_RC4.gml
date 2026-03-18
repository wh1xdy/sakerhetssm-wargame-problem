// CryptoUtils.gml

/// @function rc4(key_string, data_array)
/// @description Encrypts or decrypts an array of bytes using RC4
function rc4(_key, _data_array) {
    // 1. Key-Scheduling Algorithm (KSA)
    var _s = array_create(256);
    for (var i = 0; i < 256; i++) {
        _s[i] = i;
    }

    var _j = 0;
    var _key_len = string_length(_key);
    
    for (var i = 0; i < 256; i++) {
        // GML strings are 1-indexed!
        var _char_idx = (i % _key_len) + 1; 
        var _key_byte = ord(string_char_at(_key, _char_idx));

        _j = (_j + _s[i] + _key_byte) % 256;

        // Swap S[i] and S[j]
        var _temp = _s[i];
        _s[i] = _s[_j];
        _s[_j] = _temp;
    }

    // 2. Pseudo-Random Generation Algorithm (PRGA)
    var _data_len = array_length(_data_array);
    var _out = array_create(_data_len);
    
    var _i_idx = 0;
    var _j_idx = 0;

    for (var l = 0; l < _data_len; l++) {
        _i_idx = (_i_idx + 1) % 256;
        _j_idx = (_j_idx + _s[_i_idx]) % 256;

        // Swap
        var _temp = _s[_i_idx];
        _s[_i_idx] = _s[_j_idx];
        _s[_j_idx] = _temp;

        // Get Keystream Byte
        var _k = _s[(_s[_i_idx] + _s[_j_idx]) % 256];
        
        // XOR with Data
        _out[l] = _data_array[l] ^ _k;
    }

    return _out;
}

/// @function string_to_bytes(str)
function string_to_bytes(_str) {
    var _len = string_length(_str);
    var _arr = array_create(_len);
    for (var i = 0; i < _len; i++) {
        _arr[i] = ord(string_char_at(_str, i + 1));
    }
    return _arr;
}

/// @function bytes_to_string(arr)
function bytes_to_string(_arr) {
    var _str = "";
    for (var i = 0; i < array_length(_arr); i++) {
        _str += chr(_arr[i]);
    }
    return _str;
}