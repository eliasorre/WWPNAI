#include "bytecode_buffer.h"

#include <algorithm>
#include <random>
void BYTECODE_BUFFER::initialize()
{
  for (uint8_t i = 0; i < static_cast<uint8_t>(BYTECODE_BUFFER_NUM); i++) {
    buffers.push_back(BB_ENTRY{i});
  }
}

bool BYTECODE_BUFFER::hitInBB(uint64_t sourceMemoryAddr)
{
  BB_ENTRY* entry = hit(sourceMemoryAddr);
  if (entry == nullptr) {
    stats.miss++;
    if constexpr (BB_DEBUG_LEVEL > 2)
      fmt::print("[BYTECODE BUFFER] Missed on address {} - Total misses in BB: {} -> {}%\n", sourceMemoryAddr, stats.miss,
                 (stats.miss * 100) / (stats.miss + stats.hits));
    return false;
  }
  stats.hits++;
  if constexpr (BB_DEBUG_LEVEL > 2)
    fmt::print("[BYTECODE BUFFER] Hit on address {} - Total hits in BB: {} -> {}%\n", sourceMemoryAddr, stats.hits,
               (stats.hits * 100) / (stats.miss + stats.hits));
  decrementLRUs();
  entry->lru++;
  entry->hits++;
  entry->hits_since_last_switch++;
  return true;
}

bool BYTECODE_BUFFER::shouldFetch(uint64_t baseAddr)
{
  for (BB_ENTRY& entry : buffers) {
    if constexpr (BB_DEBUG_LEVEL > 2)
      fmt::print("[BYTECODE BUFFER] Checking fetching on entry, fetching {}, lru {}, valid {}, baseaddr {}, maxaddr {} \n", entry.fetching, entry.lru,
                 entry.valid, entry.baseAddr, entry.maxAddr);
    if (entry.hit(baseAddr) && entry.fetching) {
      stats.aggressive_prefetches++;
    }
    if (entry.hit(baseAddr)) {
      return false;
    }
    if (entry.currentlyFetching(baseAddr)) {
      return false;
    }
  }
  return true;
}

void BYTECODE_BUFFER::fetching(uint64_t baseAddr, uint64_t currentCycle, bool hitInBB)
{
  auto victim = find_victim(hitInBB);
  if (victim != nullptr) {
    victim->fetch(baseAddr, currentCycle);
    victim->prefetch = hitInBB;
    if constexpr (BB_DEBUG_LEVEL > 1)
      fmt::print("[BYTECODE BUFFER] Starting fetching in BB: {}, victim: {},  \n", baseAddr, victim->index);
    if (hitInBB) stats.prefetches++;
    return;
  }
  // Correct if no victims and we are dealing with a prefetch
  if (hitInBB) return; 
  fmt::print(stderr, "[BYTECODE BUFFER] Found no vitim {} \n", baseAddr);
  printInterestingThings();
}

bool BYTECODE_BUFFER::currentlyFetching(uint64_t baseAddr)
{
  for (BB_ENTRY const& entry : buffers) {
    if (entry.currentlyFetching(baseAddr))
      return true;
  }
  return false;
}

bool BYTECODE_BUFFER::updateBufferEntries(uint64_t baseAddr, uint64_t currentCycle)
{
  bool currFetchingFound = false;
  bool alreadyFetched = hit(baseAddr);

  auto initial_entry = std::find_if(buffers.begin(), buffers.end(), [baseAddr](BB_ENTRY entry) { return entry.currentlyFetching(baseAddr & ~1); });
  if (initial_entry == buffers.end()) {
    if (!alreadyFetched) {
      fmt::print(stderr, "Big error \n");
      exit(1);
    }
    return false;
  }
  auto entryToUpdate = &(*initial_entry);
  for (auto& entry : buffers) {
    if (entry.currentlyFetching(baseAddr & ~1) && (entry.fetching_base_addr < entryToUpdate->fetching_base_addr)) {
      entryToUpdate = &entry;
    }
  }
  stats.totalMissWait += currentCycle - entryToUpdate->fetchingEventCycle;
  entryToUpdate->valid = true;
  entryToUpdate->fetching = false;
  if (entryToUpdate->hits_since_last_switch == 0)
    entryToUpdate->switched_with_no_hits++;

  entryToUpdate->hits_since_last_switch = 0;
  entryToUpdate->baseAddr = entryToUpdate->fetching_base_addr;
  entryToUpdate->maxAddr = entryToUpdate->fetching_max_addr;
  entryToUpdate->lru = STARTING_LRU_VAL;
  decrementLRUs();
  entryToUpdate->lru++;
  if (entryToUpdate->hit(currFetching.second) && currFetching.first) {
    currFetchingFound = true;
  }

  for (BB_ENTRY& entry : buffers) {
    if constexpr (BB_DEBUG_LEVEL > 2)
      fmt::print("[BYTECODE BUFFER] Checking updating on entry, fetching {}, lru {}, valid {}, baseaddr {}, maxaddr {} \n", entry.fetching, entry.lru,
                 entry.valid, entry.baseAddr, entry.maxAddr);
    if (entry.currentlyFetching(baseAddr & ~1)) {
        entry.fetching = false;
        stats.duplicated_prefetches++;
    }
  }

  return currFetchingFound;
}

void BYTECODE_BUFFER::decrementLRUs()
{
  for (BB_ENTRY& entry : buffers) {
    if (entry.valid && entry.lru > 0)
      entry.lru--;
  }
}

BB_ENTRY* BYTECODE_BUFFER::hit(uint64_t sourceMemoryAddr)
{
  for (BB_ENTRY& entry : buffers) {
    if (entry.hit(sourceMemoryAddr)) {
      return const_cast<BB_ENTRY*>(&entry);
    }
  }
  return nullptr;
}

BB_ENTRY* BYTECODE_BUFFER::find_victim(bool prefetch)
{
  auto initial_entry = std::find_if(buffers.begin(), buffers.end(), [](BB_ENTRY entry) { return !entry.fetching; });
  if (initial_entry == buffers.end()) {
    auto prefetch_entry = std::find_if(buffers.begin(), buffers.end(), [](BB_ENTRY entry) { return entry.fetching && entry.prefetch; });
    if (prefetch_entry != buffers.end()) {
      auto victim = &(*prefetch_entry);
      for (auto& entry : buffers) {
        if (entry.fetching && entry.prefetch && (entry.lru < victim->lru)) {
          victim = &entry;
        }
      }
      return victim;
    }
    // Don't want to remove entires for a prefetch
    if (prefetch) {
      return nullptr;
    }
    fmt::print("[BYTECODE BUFFER] not enough lines for all prefetches \n");
    printInterestingThings();
    uint64_t fetchingCycleVictim = std::numeric_limits<uint64_t>::max();
    BB_ENTRY* victim = nullptr;
    for (auto& entry : buffers) {
      if (fetchingCycleVictim > entry.fetchingEventCycle) {
        fetchingCycleVictim = entry.fetchingEventCycle;
        victim = &entry;
      }
    }
    return victim;
  } else {
    auto victim = &(*initial_entry);
    for (auto& entry : buffers) {
      if (!entry.fetching && (entry.lru < victim->lru)) {
        victim = &entry;
      }
    }
    return victim;
  }
}

void BYTECODE_BUFFER::printInterestingThings()
{
  fmt::print("Duplicated prefetces: {}, aggressive prefetches: {} \n", stats.duplicated_prefetches, stats.aggressive_prefetches);
  for (BB_ENTRY const& entry : buffers) {
    fmt::print("[{}] Times changed out {}, hits: {}, hits since last: {}, times switched with no hits: {}, lru: {}, fetching: {}, prefetch: {}, valid: {}, "
               "currentAddr: "
               "{:x}, currentMaxAddr: {:x}, fetching_base: {:x}, fetching_max: {:x}, fetching_cycle: {} \n",
               entry.index, entry.timesSwitchedOut, entry.hits, entry.hits_since_last_switch, entry.switched_with_no_hits, entry.lru, entry.fetching,
               entry.prefetch, entry.valid, entry.baseAddr, entry.maxAddr, entry.fetching_base_addr, entry.fetching_max_addr, entry.fetchingEventCycle);
  }
}

void BYTECODE_BUFFER::generateStats()
{
  for (BB_ENTRY const& entry : buffers) {
    stats.entryStats.emplace_back(BB_ENTRY_STATS(entry.index, entry.timesSwitchedOut, entry.timesReset, entry.hits, entry.switched_with_no_hits));
  }
}

void BYTECODE_BUFFER::resetStats()
{
  BB_STATS newStats; 
  stats = newStats;
  for (BB_ENTRY &entry : buffers) {
    entry.timesReset = 0;
    entry.timesSwitchedOut = 0;
    entry.hits = 0;
    entry.switched_with_no_hits = 0;
  }
}