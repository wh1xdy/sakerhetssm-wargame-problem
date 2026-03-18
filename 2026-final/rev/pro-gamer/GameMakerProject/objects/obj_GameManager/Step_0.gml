if (solved) exit;

if (state == GAME_STATE.PLAYING) {
    var _player = instance_find(obj_Player, 0);
    if (_player == noone) exit;

    var _input_dir = -1;
    var _rw = room_width;
    var _rh = room_height;

    // Detect Boundary Hit
    if (_player.x > _rw - 16) { _input_dir = 0; trans_dir_x = -1; trans_dir_y = 0; }
    else if (_player.y < 16)  { _input_dir = 1; trans_dir_x = 0; trans_dir_y = 1; }
    else if (_player.x < 16)  { _input_dir = 2; trans_dir_x = 1; trans_dir_y = 0;  }
    else if (_player.y > _rh - 16) { _input_dir = 3; trans_dir_x = 0; trans_dir_y = -1; }

    if (_input_dir != -1) {
        // CHECK THE CTF LOGIC
        sequence_hash = (sequence_hash << int64(2)) | _input_dir;
		sequence_step += 1;
		buffer_write(sequence_buffer, buffer_u8, _input_dir)
		
		if(sequence_step == sequence_len) {
			if(sequence_hash * multi == target) {
				key = buffer_sha1(sequence_buffer, 0, sequence_step);
				solved = true;
				var _decrypted_bytes = rc4(key, encrypted_flag);
				flag_str = bytes_to_string(_decrypted_bytes);
				exit;
			} else {
				sequence_step = 0;
				sequence_hash = 0;
				buffer_delete(sequence_buffer)
				sequence_buffer = buffer_create(32, buffer_fixed, 1)
			}
		}
		
		
		
        // Start Transition
        state = GAME_STATE.TRANSITION;
        trans_progress = 0;
        
        // Spawn next room off-screen
        var _spawn_x = -trans_dir_x * _rw;
        var _spawn_y = -trans_dir_y * _rh;
        generate_room(sequence_hash, _spawn_x, _spawn_y);
    }
}
else if (state == GAME_STATE.TRANSITION) {
    // Move everything
    var _sx = trans_dir_x * trans_speed;
    var _sy = trans_dir_y * trans_speed;
	var _rw = room_width;
    var _rh = room_height;

    with (obj_Player) {  x = clamp(x +_sx, 20, _rw - 20) ;  y = clamp(y +_sy, 20, _rh - 20) }
    with (obj_Prop)   { x += _sx; y += _sy; }
	
	 bg_x += _sx;
    bg_y += _sy;
	
	  layer_x(bg_layer_id1, bg_x);
    layer_y(bg_layer_id1, bg_y);
	 layer_x(bg_layer_id2, bg_x);
    layer_y(bg_layer_id2, bg_y);
	 layer_x(bg_layer_id3, bg_x);
    layer_y(bg_layer_id3, bg_y);

    trans_progress += trans_speed;

    // Check completion (Width 640 or Height 480)
    var _limit = (trans_dir_x != 0) ? room_width : room_height;
    
    if (trans_progress >= _limit) {
        state = GAME_STATE.PLAYING;
        // Cleanup old props
        with (obj_Prop) {
            if (x < -16 || y < -16 || x > room_width+16 || y > room_height+16) {
                instance_destroy();
            }
        }
		
		bg_x = 0;
        bg_y = 0;
       
	   layer_x(bg_layer_id1, 0);
        layer_y(bg_layer_id1, 0);
		
		  layer_x(bg_layer_id2, 0);
        layer_y(bg_layer_id2, 0);
		
		  layer_x(bg_layer_id3, 0);
        layer_y(bg_layer_id3, 0);
    }
}
