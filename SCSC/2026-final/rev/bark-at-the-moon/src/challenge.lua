-- Configuration
local KEY = "Listen in awe and you will hear him"

local N=31
local ENC_PARAMS="514cb30e6f1ea38d6d607ada4bc09a09d741a911c052d6614c6480553664b7f4ac08f6304bb89c8c1a6c1fa4b40fc7a913f5016524aac7e4b47527fc2c7b"
local ENC_TARGET="b830eb51b44c790dfdba4f678a67d86a5be6d9569240c50846d8851cc81a1d"

-- Capture the input from C (via the '...' vararg)
local input = ...

-- 1. Basic validation
if (not input) or #input ~= N then
    return false
end

-- 2. Decrypt the parameters for the coroutines
-- hexdecode and rc4 are provided by the C host
local params_raw = crypt(hexdecode(ENC_PARAMS), KEY)

-- 3. Define the coroutine "factory"
-- This performs a bijective transformation: (x + b1) XOR b2
local function spawn_transformer(b1, b2)
    return coroutine.create(function(val)
        while true do
            -- Perform transformation
            local transformed = ((val + b1) % 256) ~ b2
            -- Yield the result and wait for the next input (if reused)
            val = coroutine.yield(transformed)
        end
    end)
end

-- 4. Process the input through the coroutines
local results = {}
for i = 1, N do
    -- Extract the two bytes for this specific character's coroutine
    local b1 = params_raw:byte(i * 2 - 1)
    local b2 = params_raw:byte(i * 2)

    -- Create the coroutine
    local co = spawn_transformer(b1, b2)

    -- Feed the user's input byte into the coroutine
    local input_byte = input:byte(i)
    local status, output_byte = coroutine.resume(co, input_byte)

    if not status then return false end

    results[i] = string.char(output_byte)
end

local final_transformed = table.concat(results)

-- 5. Decrypt the target value to compare against
local target_decoded = crypt(hexdecode(ENC_TARGET), KEY)

-- 6. Final Verification
if final_transformed == target_decoded then
    return true
else
    return false
end
