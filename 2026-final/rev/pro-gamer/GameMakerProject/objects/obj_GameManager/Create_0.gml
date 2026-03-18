randomize(); // Seed the RNG for non-gameplay stuff


state = GAME_STATE.PLAYING;

encrypted_flag = [214, 84, 149, 167, 182, 77, 111, 159, 150, 52, 192, 180, 88, 249, 81, 230, 85, 39]

// CTF DATA
// 0=Right, 1=Up, 2=Left, 3=Down
sequence_hash = int64(0);
sequence_step = 0;
sequence_buffer = buffer_create(32, buffer_fixed, 1)
solved = false;
flag_str = "";

sequence_len = 32
multi = int64(8686284858880037379)
target = int64(8284347774897715207)

// TRANSITION VARS
trans_dir_x = 0;
trans_dir_y = 0;
trans_speed = 4;
trans_progress = 0;


// METHOD: GENERATE ROOM
// We define this as a method variable so it's scoped to this instance
generate_room = function(_seed, _off_x, _off_y) {
    // Deterministic seeding based on current puzzle step
    random_set_seed(12345 + _seed * 77); 
    
    var _count = irandom_range(4, 8);
    for (var i = 0; i < _count; i++) {
        var _obj = choose(obj_Rock, obj_Bush);
        // Keep props within standard room bounds (assuming 640x480 room)
        var _rx = irandom_range(16, room_width - 16);
        var _ry = irandom_range(16, room_height - 16);
        
        instance_create_layer(_rx + _off_x, _ry + _off_y, "Instances", _obj);
    }
    randomize(); // Reset RNG
};

// Generate initial room
generate_room(sequence_hash, 0, 0);

if (!audio_is_playing(music_Background)) {
    // audio_play_sound(index, priority, loop);
    // Priority: Higher numbers = more important (if channels run out)
    // Loop: true = repeat forever
    audio_play_sound(music_Background, 1000, true);
}

// Spawn the player programmatically
// Arguments: x, y, layer_name, object_type
var _spawn_x = room_width / 2;
var _spawn_y = room_height / 2;

instance_create_layer(_spawn_x, _spawn_y, "Instances", obj_Player);


bg_layer_id1 = layer_get_id("Ground"); 
bg_layer_id2 = layer_get_id("ForestBorder"); 
bg_layer_id3 = layer_get_id("Trees"); 

// Track current offset
bg_x = 0;
bg_y = 0;