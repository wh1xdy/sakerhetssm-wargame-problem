// --- 1. GAME STATE CHECK ---
// Don't move if the room is sliding or the game is won
if (instance_exists(obj_GameManager)) {
    // Access the manager instance
    var _mgr = instance_find(obj_GameManager, 0);
    
    // Check if variables exist (safety) and check state
    if (variable_instance_exists(_mgr, "state")) {
        // Assuming your enum is global as discussed before
        if (_mgr.state == GAME_STATE.TRANSITION) exit; 
    }
    if (variable_instance_exists(_mgr, "solved")) {
        if (_mgr.solved) exit;
    }
}

// --- 2. INPUT HANDLING ---
// Returns 1, 0, or -1
var _hinput = keyboard_check(vk_right) - keyboard_check(vk_left);
var _vinput = keyboard_check(vk_down) - keyboard_check(vk_up);

// --- 3. MOVEMENT ---
x += _hinput * move_speed;
y += _vinput * move_speed;

// --- 4. ANIMATION STATE MACHINE ---

// Are we moving?
if (_hinput != 0 || _vinput != 0) {
    
    // Play animation
    image_speed = 1; 

    // VERTICAL CHECKS
    if (_vinput > 0) {
        sprite_index = spr_PlayerDown;
    } 
    else if (_vinput < 0) {
        sprite_index = spr_PlayerUp;
    }

    // HORIZONTAL CHECKS
    // Note: We place Horizontal *after* Vertical. 
    // This means if the player holds DOWN and RIGHT, they will face RIGHT.
    // This is standard "Zelda" behavior (Side-facing preference).
    if (_hinput > 0) {
        sprite_index = spr_PlayerRight;
    } 
    else if (_hinput < 0) {
        sprite_index = spr_PlayerLeft;
    }

} 
else {
    // IDLE STATE
    image_speed = 0; // Stop the animation cycle
    image_index = 0; // Force the frame to the "Standing" pose (usually index 0)
}
