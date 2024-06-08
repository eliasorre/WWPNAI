#ifdef CHAMPSIM_MODULE
#define SET_ASIDE_CHAMPSIM_MODULE
#undef CHAMPSIM_MODULE
#endif

#ifndef BYTECODE_MODULE_H
#define BYTECODE_MODULE_H

#include <algorithm>
#include <chrono>
#include <cmath>
#include <numeric>
#include <map>

#include "cache.h"
#include "champsim.h"
#include "deadlock.h"
#include "instruction.h"
#include "bytecode_buffer.h"
#include "bytecode_hdbt.h"
#include "util/span.h"
#include <fmt/chrono.h>
#include <fmt/core.h>
#include <fmt/ranges.h>

constexpr std::size_t BYTECODE_BTB_SIZE = 256;
constexpr int STARTING_BBTB_LRU_VAL = 1 << 12;

struct btb_entry_stats {
  uint64_t hit{0}, miss{0};
};

struct BYTCODE_MODULE_STATS {
    uint64_t strongly_correct = 0;
    uint64_t weakly_correct = 0;
    uint64_t wrong = 0;

    uint64_t very_large_jumps = 0;
    uint64_t large_jumps = 0;
    uint64_t small_jumps = 0;

    std::map<int, btb_entry_stats> dbtb_entryStats = {};
    double BTB_PERCENTAGE = 0;
};

class BYTECODE_MODULE {
    uint32_t cpu = 0;
    
    int last_branch_opcode; 
    int last_branch_oparg; 

    uint64_t last_bpc, last_prediction;

    bool make_btb_prediction(int opcode, int oparg);
    int64_t btb_prediction(int opcode, int oparg);
    void update_btb(int opcode, int oparg, int64_t correct_jump);
    void generateDBTBStats();
    void resetDBTBStats();
    
    public: 
        BYTECODE_BUFFER bb_buffer;
        BYTCODE_MODULE_STATS stats;
        BYTECODE_HDBT hdbt;
        void printBTBs();
        void generateStats();
        void resetStats();

        void initialize(uint32_t cpu);
        uint64_t predict_branching(int opcode, int oparg,  uint64_t current_bpc);
        bool correctPrediction(uint64_t correct_target);
};


#endif