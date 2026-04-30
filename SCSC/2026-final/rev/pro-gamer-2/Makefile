GBDK_HOME ?= $(HOME)/tools/gbdk
LCC        = $(GBDK_HOME)/bin/lcc

# Compiler/linker flags:
#   -Wa-l         : generate listing file
#   -Wl-m         : generate map file
#   -Wl-j         : enable autobanking (linker places BANKED code in correct banks)
#   -Wl-yt1       : MBC type 0x01 = MBC1 (ROM + RAM, 2 Mbit ROM)
#   -Wl-yo4       : 4 ROM banks (32 KB)
#   -Wl-ya0       : 0 RAM banks (no SRAM)
LCCFLAGS = -Wa-l -Wl-m -Wl-j -Wl-yt1 -Wl-yo4 -Wl-ya0

SRCS   = src/main.c src/game_data.c src/checker.c src/flag_data.c
TARGET = challenge.gb
GENFLG = include/flag_data.h include/enc_flag_data.h include/wram_template.h

.PHONY: all clean gen

all: $(TARGET)

# Build the ROM — requires flag_data.h to be generated first
$(TARGET): $(SRCS) $(GENFLG)
	$(LCC) $(LCCFLAGS) -o $@ $(SRCS)

# Convenience target to regenerate the flag header with a custom flag/sequence.
# Override FLAG and SEQ on the command line, e.g.:
#   make gen FLAG="CTF{my_flag_here______}" SEQ="NESWNESW"
FLAG ?= SCSC{achi3v3ment_unl0ck3d}
# ''.join(random.choices("NWSE", k=12))
SEQ  ?= NNWSENESNN
gen:
	python3 gen_flag.py --flag "$(FLAG)" --seq "$(SEQ)"

# Guard: if any generated header doesn't exist, fail with a helpful message
include/flag_data.h include/enc_flag_data.h include/wram_template.h:
	@echo ""
	@echo "  ERROR: Generated headers not found."
	@echo "  Run:  make gen FLAG=\"CTF{your_flag_here}\" SEQ=\"XXXXXXXX\""
	@echo "  Then: make"
	@echo ""
	@exit 1

clean:
	rm -f $(TARGET) *.map *.noi *.lst src/*.lst src/*.s src/*.o
