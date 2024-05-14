#include "bytecode_hdbt.h"

#include <algorithm>
#include <random>
void BYTECODE_HDBT::initialize() {}

bool BYTECODE_HDBT::hit(int opcode)
{
  auto entry = std::find_if(table.begin(), table.end(), [opcode](HDBT_ENTRY entry) { return entry.opcode == opcode; });
  if (entry != table.end()) {
    if (entry->valid) {
      entry->hits++;
      stats.hits++;
      decrementLRUs();
      entry->lru = STARTING_HDBT_LRU_VAL;
      return true;
    } else {
      entry->valid = true;
      entry->lru = STARTING_HDBT_LRU_VAL;
      entry->miss++;
    }
  }
  auto victim = find_victim();
  if (victim != nullptr) {
    victim->valid = false;
    victim->timesSwitchedOut++;
  }
  decrementLRUs();
  if (entry == table.end()) {
    table.push_back({opcode});
  }
  stats.miss++;
  return false;
}

void BYTECODE_HDBT::decrementLRUs()
{
  for (auto& entry : table) {
    if (entry.valid && entry.lru > 0)
      entry.lru--;
  }
}

HDBT_ENTRY* BYTECODE_HDBT::find_victim()
{
  if (table.size() < HDBT_SIZE) {
    return nullptr;
  }
  auto initial_entry = std::find_if(table.begin(), table.end(), [](HDBT_ENTRY entry) { return entry.valid; });

  for (auto& entry : table) {
    auto victim = &(*initial_entry);
    for (auto& entry : table) {
      if (entry.valid && (entry.lru < victim->lru)) {
        victim = &entry;
      }
    }
    return victim;
  }
  return nullptr;
}

void BYTECODE_HDBT::generateStats()
{
  for (auto const& entry : table) {
    stats.entryStats.emplace_back(HDBT_ENTRY_STATS(entry.opcode, entry.timesSwitchedOut, entry.hits, entry.miss));
  }
}