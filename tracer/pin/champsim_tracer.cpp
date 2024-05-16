/*
 *    Copyright 2023 The ChampSim Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/*! @file
 *  This is an example of the PIN tool that demonstrates some basic PIN APIs
 *  and could serve as the starting point for developing your first PIN tool
 */

#include <atomic>
#include <chrono>
#include <fcntl.h>
#include <fstream>
#include <iostream>
#include <random>
#include <set>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <map>

#include "../../inc/trace_instruction.h"
#include "pin.H"
#include "CONSTANTS.h"

using trace_instr_format_t = bytecode_instr;

/* ================================================================== */
// Global variables
/* ================================================================== */

UINT64 instrCount = 0;
std::map<std::string, UINT64> instrCounts;
UINT64 tracedInstrCount = 0;

std::ofstream outfile;
std::map<std::string, std::ofstream> outfiles;
std::ofstream debugFile;
int pipeIn;
auto start = std::chrono::high_resolution_clock::now();
PIN_THREAD_UID threadUid;

trace_instr_format_t curr_instr;

/* ===================================================================== */
// Command line switches
/* ===================================================================== */
KNOB<std::string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool", "o", "champsim.trace", "specify file name for Champsim tracer output");

KNOB<UINT64> KnobSkipInstructions(KNOB_MODE_WRITEONCE, "pintool", "s", "0", "How many instructions to skip before tracing begins");

KNOB<BOOL> KnobWaitOnPipeSignal(KNOB_MODE_WRITEONCE, "pintool", "p", "false", "Should the tool wait on pipe to write.");
KNOB<BOOL> KnobThreadSpecific(KNOB_MODE_WRITEONCE, "pintool", "m", "false", "Should the tool differentiate between threads.");
KNOB<BOOL> KnobUseFileOutput(KNOB_MODE_WRITEONCE, "pintool", "f", "false", "Should the tool write output to file.");

KNOB<UINT64> KnobTraceInstructions(KNOB_MODE_WRITEONCE, "pintool", "t", "1000000", "How many instructions to trace");
KNOB<UINT64> KnobSleepTime(KNOB_MODE_WRITEONCE, "pintool", "-sleep", "200", "How many milliseconds to sleep between each sample");

/* ===================================================================== */
// Utilities
/* ===================================================================== */

PIN_MUTEX pinLock; // Mutex that will be used to synchronize threads
/*!
 *  Print out help message.
 */
INT32 Usage()
{
  std::cerr << "This tool creates a register and memory access trace" << std::endl
            << "Specify the output trace file with -o" << std::endl
            << "Specify the number of instructions to skip before tracing with -s" << std::endl
            << "Specify the number of instructions to trace with -t" << std::endl
            << std::endl;

  std::cerr << KNOB_BASE::StringKnobSummary() << std::endl;

  return -1;
}

/* ===================================================================== */
// Analysis routines
/* ===================================================================== */

// Addresses used for knowing mainModule memory range
ADDRINT mainModuleBase = 0;
ADDRINT mainModuleHigh = 0;
uint64_t seenInstructions = 0;
uint64_t seenBytecodes = 0;
int seenTableLoads = 0;
bool startTracing = false;
bool pipeStatus = false;
INT mainProcessID = 0; // PIN_GetPid	(		)	
std::set<INT> processIDs;
PIN_THREAD_UID mainThread;
std::set<PIN_THREAD_UID> threadIDs;
OS_THREAD_ID mainOsThread;
std::set<THREADID> OSthreadIDs;


// Callback for loaded images - to find the base and high of the program, and thus calculate offsets
VOID Image(IMG img, VOID* v)
{
  if (IMG_IsMainExecutable(img)) {
    mainModuleBase = IMG_LowAddress(img);
    mainModuleHigh = IMG_HighAddress(img);
  }
}

void ResetCurrentInstruction(VOID* ip)
{
  PIN_MutexLock(&pinLock);
  seenInstructions++;
  curr_instr = {};
  curr_instr.ip = (unsigned long long int)ip;
  curr_instr.ld_type = load_type::NOT_LOAD;
  curr_instr.load_size = 0;
  curr_instr.load_val = 0;
}

VOID updatePipeStatus(const std::string& input)
{
  std::cout << input << std::endl;
  if (input == "start\n") {
    pipeStatus = true;
    std::cout << "New pipestatus: " << pipeStatus << std::endl;
  } else if (input == "stop\n") {
    pipeStatus = false;
    std::cout << "New pipestatus: " << pipeStatus << std::endl;
  } else {
    outfile.close();
    std::string str = input;
    str.erase(std::remove(str.begin(), str.end(), '\n'), str.cend());
    outfile.open(str, std::ios_base::binary | std::ios_base::trunc);
    if (!outfile) {
      std::cout << "Couldn't open output trace file. Exiting." << std::endl;
      exit(1);
    }
    std::cout << "New tracefile: " << str << "\n";
  }
}

VOID getPipeStatus()
{
  if (!KnobWaitOnPipeSignal)
    return;
  char buffer[1024];
  ssize_t bytesRead = read(pipeIn, buffer, sizeof(buffer) - 1);
  if (bytesRead > 0) {
    buffer[bytesRead] = '\0'; // Null-terminate the string
    updatePipeStatus(buffer);
  }
}

BOOL ShouldWrite()
{
  if (!startTracing || !pipeStatus)
    return false;
  if (instrCount < KnobSkipInstructions.Value()) return false;
  if (instrCount <= (KnobTraceInstructions.Value() + KnobSkipInstructions.Value())) return true;
  return false;
}

void WriteCurrentInstruction()
{
    if (KnobThreadSpecific && mainOsThread == 0) {
      std::cout << "OS thread ID: " << PIN_GetTid() << std::endl;
      mainOsThread = PIN_GetTid();
    }

    if (KnobThreadSpecific && PIN_GetTid() != mainOsThread) {
      if (OSthreadIDs.find(PIN_GetTid()) == OSthreadIDs.end()) {
        std::ofstream file;
        std::string fileName; 
        fileName.append(KnobOutputFile.Value().c_str()).append("_").append(std::to_string(PIN_GetTid()));
        file.open(fileName, std::ios_base::binary | std::ios_base::trunc);  // Explicitly using std::ios::out to open for writing
        if (file.is_open()) {
            std::cout << "Opened " << fileName << " for writing.\n";
            outfiles[std::to_string(PIN_GetTid())] = std::move(file);
        } else {
            std::cout << "Failed to open " << fileName << ". Check permissions or path.\n";
        }
        OSthreadIDs.insert(PIN_GetTid());
        std::cout << "OS-Thread IDs: ";
        for (auto threadID : OSthreadIDs) {
          std::cout << " " << threadID;
        }
        std::cout << std::endl;
      }
    }

    if (instrCount > (KnobTraceInstructions.Value() + KnobSkipInstructions.Value())) {
        PIN_MutexUnlock(&pinLock);
        PIN_ExitApplication(0);  // Ensure all threads and resources are correctly managed before this call
        return;  // This is assumed never to be reached; ensure PIN_ExitApplication is terminal
    };
    if (!ShouldWrite()) {
        PIN_MutexUnlock(&pinLock);
        return;
    }

    if (KnobThreadSpecific && PIN_GetTid() != mainOsThread) {
        if (instrCounts[std::to_string(PIN_GetTid())] < KnobTraceInstructions.Value() + KnobSkipInstructions.Value()) {
          instrCounts[std::to_string(PIN_GetTid())]++;
          if (!outfiles[std::to_string(PIN_GetTid())].is_open()) std::cout << "Failed to open after creation. Check permissions or path.\n";
          outfiles[std::to_string(PIN_GetTid())].write(reinterpret_cast<const char*>(&curr_instr), sizeof(trace_instr_format_t));
        }
        PIN_MutexUnlock(&pinLock);
        return;
    } else {
      outfile.write(reinterpret_cast<const char*>(&curr_instr), sizeof(trace_instr_format_t));
      if (!outfile) {
          std::cout << "Failed to write to file." << std::endl;
          PIN_MutexUnlock(&pinLock);
          return;
      }
      ++instrCount;
      PIN_MutexUnlock(&pinLock);
      return;
    }
}

void BranchOrNot(UINT32 taken, BOOL isStandardJumpPoint, BOOL isCombinedJump)
{
  curr_instr.is_branch = 1;
  curr_instr.branch_taken = taken;
  if (isStandardJumpPoint) curr_instr.ld_type = load_type::JUMP_POINT;
  if (isCombinedJump) curr_instr.ld_type = load_type::COMBINED_JUMP;
}

void NotSkip() { curr_instr.ld_type = load_type::NOT_SKIP; }
void Initial_Dispatch() { curr_instr.ld_type = load_type::INITIAL_POINT; }

template <typename T>
void WriteToSet(T* begin, T* end, UINT32 r)
{
  auto set_end = std::find(begin, end, 0);
  auto found_reg = std::find(begin, set_end, r); // check to see if this register is already in the list
  *found_reg = r;
}

// Determine what type of load the memory read is
void MemoryLoadType(BOOL bytecodeLoad, BOOL dispatchTableLoad)
{
  if (!ShouldWrite())
    return;
  if (bytecodeLoad) {
    seenBytecodes++;
    curr_instr.ld_type = load_type::BYTECODE;
  } else if (dispatchTableLoad) {
    seenTableLoads++;
    curr_instr.ld_type = load_type::DISPATCH_TABLE;
  } else {
    if (curr_instr.ld_type == load_type::NOT_LOAD) curr_instr.ld_type = load_type::STANDARD_DATA;
  }
}

/* ===================================================================== */
// Used for debbuing purposes
/* ===================================================================== */
template <typename T>
VOID foundByteCode(T readValue, ADDRINT PC, ADDRINT readAddr, UINT32 readSize, BOOL bytecode)
{
  if (PIN_SafeCopy(readValue, reinterpret_cast<void*>(readAddr), readSize) == readSize) {
    UINT64 loaded_val;
    if (readSize == 1)
      loaded_val = static_cast<UINT64>(*readValue & 0xFF);
    else if (readSize == 2)
      loaded_val = static_cast<UINT64>(*readValue & 0xFFFF);
    else
      loaded_val = static_cast<UINT64>(*readValue);
    curr_instr.load_val = loaded_val;
    curr_instr.load_size = readSize * 8;
  }
  MemoryLoadType(bytecode, !bytecode);
}

VOID ByteCodeLoad(ADDRINT PC, ADDRINT readAddr, UINT32 readSize, BOOL bytecode)
{
  if (readSize == 8) {
    UINT64 readValue;
    foundByteCode(&readValue, PC, readAddr, readSize, bytecode);
  } else if (readSize == 4) {
    UINT32 readValue;
    foundByteCode(&readValue, PC, readAddr, readSize, bytecode);
  } else if (readSize == 2) {
    UINT16 readValue;
    foundByteCode(&readValue, PC, readAddr, readSize, bytecode);
  } else if (readSize == 1) {
    UINT8 readValue;
    foundByteCode(&readValue, PC, readAddr, readSize, bytecode);
  }
}

/* ===================================================================== */
// Instrumentation callbacks
/* ===================================================================== */

// Is called for every instruction and instruments reads and writes
VOID Instruction(INS ins, VOID* v)
{
  if (INS_Address(ins) == 0) {
    std::cout << "INS addr 0!" << std::endl;
    exit(255);
  }
  // begin each instruction with this function
  INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)ResetCurrentInstruction, IARG_INST_PTR, IARG_END);
  
  ADDRINT insAddr = INS_Address(ins) - mainModuleBase;
  // instrument branch instructions
  if (INS_IsBranch(ins)) {
    bool isStandardJumpPoint = NORMAL_DISPATCH_JUMP.find(insAddr) != NORMAL_DISPATCH_JUMP.end();
    bool isCombinedJumpPoint = COMBINED_DISPATCH_JUMPS.find(insAddr) != COMBINED_DISPATCH_JUMPS.end();
    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)BranchOrNot, IARG_BRANCH_TAKEN, IARG_BOOL, isStandardJumpPoint, IARG_BOOL, isCombinedJumpPoint, IARG_END);
  }

  // notSkipOrInitial
  if (NOT_SKIP_INSTRS.find(insAddr) != NOT_SKIP_INSTRS.end()) {
    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)NotSkip, IARG_END);
  } else if (INITIAL_INSTRS.find(insAddr) != INITIAL_INSTRS.end()) {
    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)Initial_Dispatch, IARG_END);
  }

  if (BYTECODE_INSTR.find(insAddr) != BYTECODE_INSTR.end()) {
    if (INS_IsMemoryRead(ins) == false) {
      std::cout << "Bytecode load is not load!" << std::endl;
      exit(255);
    }
    else if(!(INS_Address(ins) < mainModuleHigh && INS_Address(ins) >= mainModuleBase))
      {
        std::cout << "Bytecode load is outside mainModuleBase load!" << std::endl;
        exit(255);
      }
    // Start tracing when encountering bytecodes
    if (!startTracing)
      startTracing = true;
    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)ByteCodeLoad, IARG_INST_PTR, IARG_MEMORYREAD_EA, IARG_UINT32, INS_MemoryOperandSize(ins, 0), IARG_BOOL, true,
                   IARG_END);
  } else if (DISPATCH_TABLE_INSTRS.find(insAddr) != DISPATCH_TABLE_INSTRS.end()) {
    if (INS_IsMemoryRead(ins) == false) {
      std::cout << "Dispatch load is not load!" << std::endl;
      exit(255);
    }
    else if (!(INS_Address(ins) < mainModuleHigh && INS_Address(ins) >= mainModuleBase))
      {
        std::cout << "Dispatch load is outside mainModuleBase load!" << std::endl;
        exit(255);
      }
    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)ByteCodeLoad, IARG_INST_PTR, IARG_MEMORYREAD_EA, IARG_UINT32, INS_MemoryOperandSize(ins, 0), IARG_BOOL, false,
                   IARG_END);
  } else {
    if (INS_IsMemoryRead(ins))
      INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)MemoryLoadType, IARG_BOOL, false, IARG_BOOL, false, IARG_END);
  }

  // instrument register reads
  UINT32 readRegCount = INS_MaxNumRRegs(ins);
  for (UINT32 i = 0; i < readRegCount; i++) {
    UINT32 regNum = INS_RegR(ins, i);
    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)WriteToSet<unsigned char>, IARG_PTR, curr_instr.source_registers, IARG_PTR,
                   curr_instr.source_registers + NUM_INSTR_SOURCES, IARG_UINT32, regNum, IARG_END);
  }

  // instrument register writes
  UINT32 writeRegCount = INS_MaxNumWRegs(ins);
  for (UINT32 i = 0; i < writeRegCount; i++) {
    UINT32 regNum = INS_RegW(ins, i);
    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)WriteToSet<unsigned char>, IARG_PTR, curr_instr.destination_registers, IARG_PTR,
                   curr_instr.destination_registers + NUM_INSTR_DESTINATIONS, IARG_UINT32, regNum, IARG_END);
  }

  // instrument memory reads and writes
  UINT32 memOperands = INS_MemoryOperandCount(ins);

  // Iterate over each memory operand of the instruction.
  for (UINT32 memOp = 0; memOp < memOperands; memOp++) {
    if (INS_MemoryOperandIsRead(ins, memOp))
      INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)WriteToSet<unsigned long long int>, IARG_PTR, curr_instr.source_memory, IARG_PTR,
                     curr_instr.source_memory + NUM_INSTR_SOURCES, IARG_MEMORYOP_EA, memOp, IARG_END);
    if (INS_MemoryOperandIsWritten(ins, memOp))
      INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)WriteToSet<unsigned long long int>, IARG_PTR, curr_instr.destination_memory, IARG_PTR,
                     curr_instr.destination_memory + NUM_INSTR_DESTINATIONS, IARG_MEMORYOP_EA, memOp, IARG_END);
  }

  INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)WriteCurrentInstruction, IARG_END);
}

VOID checkIn() {
  PIN_MutexLock(&pinLock);
  getPipeStatus();
  std::cout << "Current value of instructions seen: " << std::dec << seenInstructions << " seen bytecodes: " << seenBytecodes
      << " traced instructions: main thread: " << instrCount;
  for (auto counts : instrCounts) {
    std::cout << " Tid: " << counts.first << " traced: " << counts.second;
  }
  std::cout << std::endl;
  PIN_MutexUnlock(&pinLock);
}

BOOL monitor = true;
static VOID MonitorExecution(VOID* arg)
{
  while (monitor) {
    PIN_Sleep(KnobSleepTime.Value());
    checkIn();
  }
}

/*!
 * Print out analysis results.
 * This function is called when the application exits.
 * @param[in]   code            exit code of the application
 * @param[in]   v               value specified by the tool in the
 *                              PIN_AddFiniFunction function call
 */
VOID Fini(INT32 code, VOID* v)
{
  monitor = false;
  INT32 threadExitCode;
  BOOL waitStatus = PIN_WaitForThreadTermination(threadUid, PIN_INFINITE_TIMEOUT, &threadExitCode);
  if (!waitStatus) {
    std::cout << "PIN_WaitForThreadTermination failed\n";
  }
  for (auto& entry : outfiles) {
    entry.second.close();
  }
  PIN_Sleep(KnobSleepTime.Value());

  outfile.close();
  debugFile << std::hex << mainModuleBase << std::endl;
  debugFile << std::dec << std::setprecision(64) << "Seen bytecodes: " << seenBytecodes << std::endl;
  debugFile << std::setprecision(64) << "Seen dispatch table loads: " << seenTableLoads << std::endl;
  debugFile << "Written instructions: " << tracedInstrCount << "\n";
  debugFile.close();


  auto end = std::chrono::high_resolution_clock::now();
  std::cout << "Execution time: " << std::setprecision(5) << ((double)std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count()) / 1000.0
            << " seconds \n";
}

/*!
 * The main procedure of the tool.
 * This function is called when the application image is loaded but not yet started.
 * @param[in]   argc            total number of elements in the argv array
 * @param[in]   argv            array of command line arguments,
 *                              including pin -t <toolname> -- ...
 */
int main(int argc, char* argv[])
{
  // Initialize PIN library. Print help message if -h(elp) is specified
  // in the command line or the command line is invalid
  if (PIN_Init(argc, argv))
    return Usage();
  if (!PIN_MutexInit(&pinLock)) std::cout << "Couldn't fix mutex \n";

  outfile.open(KnobOutputFile.Value().c_str(), std::ios_base::binary | std::ios_base::trunc);
  std::string debugFileName; 
  debugFileName.append(KnobOutputFile.Value().c_str()).append("_debug");
  debugFile.open(debugFileName);
  debugFile.setf(std::ios::showbase);
  if (!outfile) {
    std::cout << "Couldn't open output trace file. Exiting." << std::endl;
    exit(1);
  }
  if (KnobUseFileOutput) {
    freopen("tool_output.txt", "w", stdout);
  }

  if (KnobWaitOnPipeSignal) {
    std::cout << "Opening pipe! \n";
    pipeIn = open("/tmp/pinToolPipe", O_RDWR);
    int flags = fcntl(pipeIn, F_GETFL, 0);
    if (flags == -1) {
      std::cerr << "Error getting flags" << std::endl;
      return 1;
    }
    if (fcntl(pipeIn, F_SETFL, flags | O_NONBLOCK) == -1) {
      std::cerr << "Error setting non-blocking mode" << std::endl;
      return 1;
    }
    if (pipeIn == -1) {
      std::cerr << "Failed to open pipe for reading: " << std::strerror(errno) << std::endl;
      return 1;
    }
    std::cout << "Opened pipe! \n";
  } else {
    pipeStatus = true;
  }

  // Fix base adress to enable calculation of offset
  IMG_AddInstrumentFunction(Image, 0);
  // Register function to be called to instrument instructions
  INS_AddInstrumentFunction(Instruction, 0);

  // Register function to be called when the application exits
  PIN_AddFiniFunction(Fini, 0);

  start = std::chrono::high_resolution_clock::now();
  // Create a thread wich informs the user of the PIN-tools state and exectuion, and also checks for changes to the pipe flag
  PIN_SpawnInternalThread(MonitorExecution, NULL, 0, &threadUid);
  if (threadUid == INVALID_THREADID) {
    std::cout << "Error creating thread\n" << std::endl;
    return 1;
  }

  // Start the program, never returns
  PIN_StartProgram();

  return 0;
}
