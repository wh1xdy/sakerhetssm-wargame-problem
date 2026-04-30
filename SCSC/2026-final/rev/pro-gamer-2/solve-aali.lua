state = 0
setup = 5
interval = 2

keys = { C.GBA_KEY.UP, C.GBA_KEY.DOWN, C.GBA_KEY.LEFT, C.GBA_KEY.RIGHT }

cbid = 0

function scanKeys()
  emu:clearKeys(0xFFFFFFFF)

  if emu:currentFrame() == setup then
    emu:saveStateSlot(0, 0)
  end
  
  for i=1,10 do
    if emu:currentFrame() == setup + interval * i then
      emu:addKey(keys[(state >> (2 * (i - 1))) % 4 + 1])
    end
  end

  if emu:currentFrame() == setup + interval * 11 then
    if emu:read8(0xc0bf) == 0 then
      emu:loadStateSlot(0, 0)
      state = state + 1
      console:log(tostring(state))
    else
      callbacks:remove(cbid)
    end
  end
end

cbid = callbacks:add("keysRead", scanKeys)
