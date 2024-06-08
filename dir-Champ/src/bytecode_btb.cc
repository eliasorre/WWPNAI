
/*
 * This file implements a basic Branch Target Buffer (BTB) structure.
 * It uses a set-associative BTB to predict the targets of non-return branches,
 * and it uses a small Return Address Stack (RAS) to predict the target of
 * returns.
 */

#include <algorithm>
#include <bitset>
#include <deque>
#include <iostream>
#include <map>
#include <sstream>

#include "bytecode_module.h"
#include "msl/lru_table.h"
#include <fmt/ostream.h>

namespace
{

constexpr bool USE_OPARGS = false;
constexpr int MAX_USAGE_VAL = 8;
constexpr std::size_t STARTING_USAGE_VAL = 4;
constexpr int MAX_CONFIDENCE = 3;
constexpr int STARTING_CONFIDENCE = 3;

std::map<int, btb_entry_stats> entryStats = {};

struct btb_entry_t {
  int opcode = 0;
  int oparg = 0;
  int64_t jump = 0;
  bool valid = true;
  bool inner_entry = false;
  std::vector<btb_entry_t> inner_entries;

  int usage = STARTING_USAGE_VAL;
  int confidence = STARTING_CONFIDENCE;
  uint64_t lru = STARTING_BBTB_LRU_VAL;

  uint64_t hits{0}, misses{0};

  void update(int64_t correctJump)
  {
    if (valid == false)
      return;
    if (jump == 0) {
      jump = correctJump;
      return;
    }
    if (correctJump == jump) {
      correctPrediction();
    } else {
      wrongPrediction(correctJump);
    }
  }

  void correctPrediction()
  {
    if (confidence < MAX_CONFIDENCE)
      confidence++;
    if (usage < MAX_USAGE_VAL)
      usage++;
    hits++;
    entryStats[opcode].hit++;
  }

  void wrongPrediction(int64_t correctTarget)
  {
    if (confidence > 1)
      confidence--;
    else {
      confidence = STARTING_CONFIDENCE;
      jump = correctTarget;
    }
    if (usage > 0)
      usage--;
    else
      valid = false;
    misses++;
    entryStats[opcode].miss++;
  }

  btb_entry_t* findInnerEntry(int oparg)
  {
    if constexpr (!USE_OPARGS)
      return this;
    if (oparg == 0)
      return this;
    auto entry = std::find_if(inner_entries.begin(), inner_entries.end(), [oparg](btb_entry_t btb_entry) { return btb_entry.oparg == oparg; });
    if (entry == inner_entries.end())
      return nullptr;
    return &(*entry);
  }

  int64_t makePrediction(int oparg)
  {
    auto innerEntry = findInnerEntry(oparg);
    if (innerEntry == nullptr) {
      return (valid) ? jump : 0;
    }
    return (innerEntry->valid) ? innerEntry->jump : 0;
  }

  auto totalHitsAndMisses() const
  {
    uint64_t totalHits = hits;
    uint64_t totalMisses = misses;
    for (auto const& innerEntry : inner_entries) {
      totalHits += innerEntry.hits;
      totalMisses += innerEntry.misses;
    }
    return std::pair(totalHits, totalMisses);
  }

  double percentageHits() const
  {
    if (inner_entry)
      return 0;
    auto [totalHits, totalMisses] = totalHitsAndMisses();
    return 100 * (double)totalHits / ((double)totalHits + (double)totalMisses);
  }
};

std::vector<btb_entry_t> bytecode_BTB;
/*
 * The following structure identifies the size of call instructions so we can
 * find the target for a call's return, since calls may have different sizes.
 */
} // namespace

btb_entry_t* findOuterEntry(int opcode)
{
  auto entry = std::find_if(bytecode_BTB.begin(), bytecode_BTB.end(), [opcode](btb_entry_t entry) { return entry.opcode == opcode; });
  if (entry != bytecode_BTB.end())
    return &(*entry);
  return nullptr;
}

btb_entry_t* createOuterEntry(int opcode)
{
  btb_entry_t newEntry;
  newEntry.opcode = opcode;
  bytecode_BTB.emplace_back(newEntry);
  return &bytecode_BTB.back();
}

void updateLRUs() {
  for (auto &elem : bytecode_BTB) {
    elem.lru--;
  }
}

bool foundVictim()
{
  if (bytecode_BTB.size() < BYTECODE_BTB_SIZE) {
    return true;
  }
  if constexpr (BYTECODE_BTB_SIZE == 0)
    return false;
  auto victim = bytecode_BTB.front();
  for (auto& entry : bytecode_BTB) {
    if (entry.valid && (entry.lru < victim.lru)) {
      victim = entry;
    }
  }
  bytecode_BTB.erase(std::find_if(bytecode_BTB.begin(), bytecode_BTB.end(), [victim] (btb_entry_t entry) { return entry.opcode == victim.opcode; }));
  return true;
}

int64_t BYTECODE_MODULE::btb_prediction(int opcode, int oparg)
{
  if (findOuterEntry(opcode) == nullptr)
    return 0;
  return findOuterEntry(opcode)->makePrediction(oparg);
}

void BYTECODE_MODULE::update_btb(int opcode, int oparg, int64_t correct_jump)
{
  auto outerEntry = findOuterEntry(opcode);
  if (correct_jump > 16) {
    stats.very_large_jumps++;
  }
  else if (correct_jump > 4) {
    stats.large_jumps++;
  } else {
    stats.small_jumps++;
  }

  
  if (outerEntry == nullptr) {
    // No point in creating entries for standard bytecodes
    if (correct_jump == BYTECODE_SIZE)
      return;
    if (!foundVictim())
      return;
    outerEntry = createOuterEntry(opcode);
  }
  auto innerEntry = outerEntry->findInnerEntry(oparg);
  if (innerEntry == nullptr) {
    if (correct_jump != outerEntry->jump) {
      btb_entry_t newEntry;
      newEntry.opcode = opcode;
      newEntry.oparg = oparg;
      newEntry.jump = correct_jump;
      outerEntry->inner_entries.emplace_back(newEntry);
    }
    outerEntry->update(correct_jump);
    updateLRUs();
    outerEntry->lru++;
  } else {
    innerEntry->update(correct_jump);
    updateLRUs();
    innerEntry->lru++;
  }
}

void BYTECODE_MODULE::printBTBs()
{
  // Iterate over each module and its corresponding INDIRECT_BTB entries
  int moduleint = 0;
  fmt::print(stdout, "\n --- BYTECODE MODULE BTB STATS --- \n");
  uint64_t totalMisses{0}, totalHits{0};
  for (auto const& outer_entry : bytecode_BTB) {
    auto [hits, misses] = outer_entry.totalHitsAndMisses();
    totalMisses += misses;
    totalHits += hits;
  }
  auto totalPercentage = 100 * (double)totalHits / ((double)totalHits + (double)totalMisses);
  stats.BTB_PERCENTAGE = totalPercentage;

  fmt::print("BYTECODE BTB HITS: {}, MISS: {}, PERCENTAGE: {} \n", totalHits, totalMisses, totalPercentage);
  for (auto const& outer_entry : bytecode_BTB) {
    fmt::print(stdout, "Outer entry for opcode: {}, hits: {}, misses: {}, percentage: {}, prediction: {} \n \t", outer_entry.opcode, outer_entry.hits,
               outer_entry.misses, outer_entry.percentageHits(), outer_entry.jump);
    for (auto const& inner_entry : outer_entry.inner_entries) {
      fmt::print(stdout, "  [arg: {}, h: {}, m: {}, j: {}] ", inner_entry.opcode, inner_entry.hits, inner_entry.misses, inner_entry.jump);
    }
    fmt::print(stdout, "\n");
  }
  fmt::print(stdout, "---------------------------------- \n\n");
}

void BYTECODE_MODULE::generateDBTBStats()
{
  for (auto const& [opcode, btb_stats] : entryStats) {
    stats.dbtb_entryStats[opcode].hit = btb_stats.hit;
    stats.dbtb_entryStats[opcode].miss = btb_stats.miss;
  }
}

void BYTECODE_MODULE::resetDBTBStats()
{
  entryStats.clear();
}