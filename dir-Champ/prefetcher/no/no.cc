#include "cache.h"

void CACHE::prefetcher_initialize() {}

uint32_t CACHE::prefetcher_cache_operate(uint64_t addr, uint64_t ip, uint64_t instr_id, uint8_t cache_hit, bool useful_prefetch, uint8_t type, uint8_t, uint32_t metadata_in)
{
  return metadata_in;
}

uint32_t CACHE::prefetcher_cache_fill(uint64_t addr, uint32_t set, uint32_t way, uint8_t prefetch, uint64_t evicted_addr, uint32_t metadata_in)
{
  return metadata_in;
}

void CACHE::prefetcher_squash(uint64_t ip, uint64_t instr_id) {}

void CACHE::prefetcher_cycle_operate() {}

void CACHE::prefetcher_final_stats() {}