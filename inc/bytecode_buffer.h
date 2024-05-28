#ifdef CHAMPSIM_MODULE
#define SET_ASIDE_CHAMPSIM_MODULE
#undef CHAMPSIM_MODULE
#endif

#ifndef BYTECODE_BUFFER_H
#define BYTECODE_BUFFER_H

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

constexpr std::size_t BYTECODE_SIZE = 2;
constexpr int BYTECODE_BUFFER_SIZE = 16;
constexpr std::size_t BYTECODE_BUFFER_NUM = 3;
constexpr int LOG2_BB_BUFFER_SIZE = champsim::lg2(BYTECODE_BUFFER_SIZE);
constexpr uint64_t BYTECODE_FETCH_TIME = 1;
constexpr uint64_t FETCH_OFFSET = 0; // 2 * BYTECODE_FETCH_TIME;
constexpr uint64_t BYTECODE_BRANCH_MISPREDICT_PENALTY = 4;
constexpr uint64_t BB_DEBUG_LEVEL = 0; // 0 = NONE, 1 = WARNINGS, 2 = HITS AND MISSES, 3 = INFO 
constexpr int STARTING_LRU_VAL = 1 << 12;

struct BB_ENTRY_STATS {
    uint8_t index; 
    uint64_t timesSwitchedOut = 0;
    uint64_t timesReset = 0;
    uint64_t hits = 0;
    uint64_t switched_with_no_hits = 0;

    BB_ENTRY_STATS(uint8_t i, uint64_t switches, uint64_t resets, uint64_t hit, uint64_t nohit) {
        index = i;
        timesSwitchedOut = switches;
        timesReset = resets;
        hits = hit;
        switched_with_no_hits = nohit;
    }
};

struct BB_STATS {
    uint64_t hits = 0;
    uint64_t miss = 0;
    uint64_t totalMissWait = 0;
    uint64_t prefetches = 0;
    uint64_t inflightMisses = 0;
    uint64_t duplicated_prefetches = 0;
    uint64_t aggressive_prefetches = 0;
    std::vector<BB_ENTRY_STATS> entryStats = {};
    double averageWaitTime() const { return (double) totalMissWait/ (double) miss; }
};

struct BB_ENTRY {
    uint8_t index; 
    uint64_t timesSwitchedOut = 0;
    uint64_t timesReset = 0;
    uint64_t hits = 0;
    uint64_t hits_since_last_switch = 0;
    uint64_t switched_with_no_hits = 0;
    uint64_t prefetch = false;

    uint64_t baseAddr;
    uint64_t maxAddr; 
    uint64_t fetchingEventCycle = 0;
    uint64_t fetching_base_addr;
    uint64_t fetching_max_addr; 
    bool valid = false;
    bool fetching = false;
    int lru = 0; 

    bool hit(uint64_t sourceAddr) const { return ((sourceAddr >= baseAddr) && (sourceAddr <= maxAddr) && valid); }
    bool currentlyFetching(uint64_t sourceAddr) const { return ((sourceAddr >= fetching_base_addr) && (sourceAddr <= fetching_max_addr) && fetching); }
    void fetch(uint64_t sourceAddr, uint64_t currentCycle) {
        fetching = true;
        timesSwitchedOut++;
        fetching_base_addr = (sourceAddr & ~1) - (FETCH_OFFSET * BYTECODE_SIZE);
        fetching_max_addr = (sourceAddr & ~1) + ((BYTECODE_BUFFER_SIZE - FETCH_OFFSET) * BYTECODE_SIZE);
        fetchingEventCycle = currentCycle;
    }
    
    void reset() {
        fetching = false;
        lru = 0;
        timesReset++;
    }
    BB_ENTRY(uint8_t block_index) { index=block_index; }
};

class BYTECODE_BUFFER {
    std::vector<BB_ENTRY> buffers; 

    void decrementLRUs();
    BB_ENTRY* hit(uint64_t sourceMemoryAddr);
    BB_ENTRY* find_victim(bool prefetch);

 public:
    BB_STATS stats;
    std::pair<bool, uint64_t> currFetching;

    void printInterestingThings();
    void initialize();
    void generateStats();
    void resetStats();
    void fetching(uint64_t baseAddr, uint64_t currentCycle, bool hitInBB);
    bool hitInBB(uint64_t sourceMemoryAddr);
    bool shouldFetch(uint64_t sourceMemoryAddr);
    bool updateBufferEntries(uint64_t baseAddr, uint64_t currentCycle);
    bool currentlyFetching(uint64_t baseAddr);
};

#endif
