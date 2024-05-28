#ifdef CHAMPSIM_MODULE
#define SET_ASIDE_CHAMPSIM_MODULE
#undef CHAMPSIM_MODULE
#endif

#ifndef BYTECODE_HDBT_H
#define BYTECODE_HDBT_H

#include <array>
#include <bitset>
#include <deque>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#include <map>
#include <fmt/core.h>
#include <fmt/ranges.h>

#include "champsim.h"
#include "champsim_constants.h"
#include "channel.h"
#include "cache.h"
#include "operable.h"
#include <type_traits>

constexpr std::size_t HDBT_SIZE = 128;
constexpr int STARTING_HDBT_LRU_VAL = 1 << 12;

struct HDBT_ENTRY_STATS {
    int opcode; 
    uint64_t timesSwitchedOut = 0;
    uint64_t hits = 0;
    uint64_t miss = 0;

    HDBT_ENTRY_STATS(uint8_t code, uint64_t switches, uint64_t hit, uint64_t nohit) {
        opcode = code;
        timesSwitchedOut = switches;
        hits = hit;
        miss = nohit;
    }
};

struct HDBT_STATS {
    uint64_t hits = 0;
    uint64_t miss = 0;
    std::vector<HDBT_ENTRY_STATS> entryStats = {};
};

struct HDBT_ENTRY {
    int opcode; 
    uint64_t timesSwitchedOut = 0;
    uint64_t hits = 0;
    uint64_t miss = 1;

    bool valid = false;
    int lru = STARTING_HDBT_LRU_VAL; 
    
    HDBT_ENTRY(int code) { 
        opcode=code; 
        valid = true;
    }
};

class BYTECODE_HDBT {
    std::vector<HDBT_ENTRY> table; 

    void decrementLRUs();
    HDBT_ENTRY* find_victim();

 public:
    HDBT_STATS stats;
    void initialize();
    void generateStats();
    void resetStats();
    bool hit(int opcode);
};


#endif
