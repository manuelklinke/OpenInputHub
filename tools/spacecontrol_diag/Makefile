CXX ?= g++

SDK_DIR := ../../vendor/sc_treiber/SpaceControl/sdk
TARGET := spacecontrol_diag

CXXFLAGS ?= -std=c++17 -Wall -Wextra -pedantic -O2
CPPFLAGS += -isystem $(SDK_DIR)
LDFLAGS += -L$(SDK_DIR) -Wl,-rpath,'$$ORIGIN/../../vendor/sc_treiber/SpaceControl/sdk'
LDLIBS += -l:libspc_ctrl_64.so.2.9.2

.PHONY: all clean

all: $(TARGET)

$(TARGET): main.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(LDFLAGS) -o $@ $< $(LDLIBS)

clean:
	$(RM) $(TARGET)
