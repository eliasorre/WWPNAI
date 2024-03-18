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

#include <fstream>
#include <iostream>
#include <random>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <set>

#include "../../inc/trace_instruction.h"
#include "pin.H"

using trace_instr_format_t = bytecode_instr;

/* ================================================================== */
// Global variables
/* ================================================================== */

UINT64 instrCount = 0;

std::ofstream outfile;
std::ofstream debugFile; 

trace_instr_format_t curr_instr;

/* ===================================================================== */
// Command line switches
/* ===================================================================== */
KNOB<std::string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool", "o", "champsim.trace", "specify file name for Champsim tracer output");
KNOB<std::string> KnobDebugFile(KNOB_MODE_WRITEONCE, "pintool", "d", "tool_debug.out", "debug file");

KNOB<UINT64> KnobSkipInstructions(KNOB_MODE_WRITEONCE, "pintool", "s", "0", "How many instructions to skip before tracing begins");

KNOB<UINT64> KnobTraceInstructions(KNOB_MODE_WRITEONCE, "pintool", "t", "1000000", "How many instructions to trace");

/* ===================================================================== */
// Utilities
/* ===================================================================== */

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
int seenBytecodes = 0;
int seenTableLoads = 0;
bool startTracing = false;

// Callback for loaded images - to find the base and high of the program, and thus calculate offsets
VOID Image(IMG img, VOID* v) {
    if (IMG_IsMainExecutable(img)) {
        mainModuleBase = IMG_LowAddress(img);
        mainModuleHigh = IMG_HighAddress(img);
    }
}

void ResetCurrentInstruction(VOID* ip)
{
  curr_instr = {};
  curr_instr.ip = (unsigned long long int)ip;
  curr_instr.ld_type = load_type::NOT_LOAD;
}

BOOL ShouldWrite()
{
  ++instrCount;
  return (instrCount > KnobSkipInstructions.Value()) && (instrCount <= (KnobTraceInstructions.Value() + KnobSkipInstructions.Value()));
}

void WriteCurrentInstruction()
{
  if (!startTracing) return;
  typename decltype(outfile)::char_type buf[sizeof(trace_instr_format_t)];
  std::memcpy(buf, &curr_instr, sizeof(trace_instr_format_t));
  outfile.write(buf, sizeof(trace_instr_format_t));
}

void BranchOrNot(UINT32 taken)
{
  curr_instr.is_branch = 1;
  curr_instr.branch_taken = taken;
}

template <typename T>
void WriteToSet(T* begin, T* end, UINT32 r)
{
  auto set_end = std::find(begin, end, 0);
  auto found_reg = std::find(begin, set_end, r); // check to see if this register is already in the list
  *found_reg = r;
}

// Determine what type of load the memory read is
void MemoryLoadType(BOOL bytecodeLoad, BOOL dispatchTableLoad) {
  if (bytecodeLoad) {
    seenBytecodes++;    
    curr_instr.ld_type = load_type::BYTECODE;
  } else if (dispatchTableLoad) {
    seenTableLoads++;    
    curr_instr.ld_type = load_type::DISPATCH_TABLE;
  } else {
    curr_instr.ld_type = load_type::STANDARD_DATA;
  }
}

/* ===================================================================== */
// Used for debbuing purposes
/* ===================================================================== */
std::set<ADDRINT> wrongBytecodes;
template <typename T> 
VOID foundByteCode(T readValue, ADDRINT PC, ADDRINT readAddr, UINT32 readSize) {
    if (PIN_SafeCopy(readValue, reinterpret_cast<void*>(readAddr), readSize) == readSize) {
        // Print the memory read value in hex
        INT bytecode = static_cast<INT>(*readValue & 0xFF);
        INT bytecodeBigEndian = static_cast<INT>(*readValue >> 8);
        debugFile << std::dec << bytecode << " " << bytecodeBigEndian << "\n";
        if (bytecode == 0) {
          wrongBytecodes.insert(PC - mainModuleBase); 
        }
    }
    MemoryLoadType(true, false);
}


VOID ByteCodeLoad(ADDRINT PC, ADDRINT readAddr, UINT32 readSize) {
    if (readSize == 8){
        UINT64 readValue;
        foundByteCode(&readValue, PC, readAddr, readSize);
    } else if (readSize == 4) {
        UINT32 readValue;
        foundByteCode(&readValue, PC, readAddr, readSize);
    } else if (readSize == 2) {
        UINT16 readValue;
        foundByteCode(&readValue, PC, readAddr, readSize);
    }
    else if (readSize == 1) {
        UINT8 readValue;
        foundByteCode(&readValue, PC, readAddr, readSize);
    }
  } 

/* ===================================================================== */
// Instrumentation callbacks
/* ===================================================================== */

// Is called for every instruction and instruments reads and writes
VOID Instruction(INS ins, VOID* v)
{
  // begin each instruction with this function
  INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)ResetCurrentInstruction, IARG_INST_PTR, IARG_END);

  // instrument branch instructions
  if (INS_IsBranch(ins))
    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)BranchOrNot, IARG_BRANCH_TAKEN, IARG_END);

  if (INS_IsMemoryRead(ins)) {
    static const std::vector<ADDRINT> byteCodeLoadAddresses = {
      //0x25c168, 0x25c444,0x25c68e,
      0x25c2c6,0x25c58a,0x264340,0x2645f2,0x264897,0x26c661,0x26c72d,0x25bbf5,
      0x26c762,0x25bc6b,0x25bd25,0x25be2f,0x25bf0e,0x25bfe9,0x25c0bc,0x25c1fb,0x25c34e,0x25c495,0x25c5cc,0x25c721,0x25c80c,0x25c8b0,0x25c95a,0x25ca04,0x25cacf,0x25cb6b,0x25cc56,0x25cd65,0x25ceba,0x25d007,0x25d159,0x25d2ae,0x25d436,0x25d5d9,0x25d72b,0x25d853,0x25da79,0x25dcac,0x25de77,0x25e1c3,0x25e2b0,0x25e3cf,0x25e5f4,0x25e771,0x25e893,0x25e9a9,0x25ed5d,0x25ef05,0x25f05a,0x25f260,0x25f468,0x25f57f,0x25f7a5,0x25fa46,0x25fbe8,0x25fd43,0x25fe2d,0x25ffdb,0x2600ed,0x260240,0x2604e1,0x2606f7,0x2608a5,0x2609ba,0x260b38,0x260c2e,0x260d25,0x260dde,0x260efc,0x2611c2,0x2614ca,0x261690,0x261795,0x261843,0x2618ed,0x261a0c,0x261bfc,0x261ce3,0x261e1b,0x261f40,0x262069,0x262192,0x2622a1,0x2623c1,0x262535,0x2626a7,0x2628d2,0x2629b0,0x262cba,0x262d9f,0x262eee,0x263015,0x263111,0x2632de,0x2636c9,0x2634a8,0x263871,0x263aab,0x263d30,0x263ffb,0x26417b,0x2643d9,0x26468b,0x264944,0x264b70,0x264cea,0x264f0c,0x26514e,0x2652de,0x2653f2,0x26552a,0x2655c6,0x26567c,0x265739,0x2657a8,0x26583b,0x26597e,0x265ac1,0x265b2e,0x265bc1,0x265d01,0x265e2a,0x265ebe,0x265f7e,0x26605a,0x266157,0x26626e,0x2662db,0x266372,0x266486,0x2664f3,0x26658a,0x26669a,0x2667b5,0x266926,0x266aab,0x266b98,0x266c76,0x266d3d,0x266e04,0x266f03,0x267018,0x26714a,0x267311,0x2674f6,0x267640,0x2677a1,0x267a65,0x267cb6,0x267e9d,0x2680b1,0x2682c4,0x2683f5,0x268559,0x26860b,0x2686b3,0x268a11,0x268c0f,0x269370,0x269532,0x2696e2,0x269974,0x269b9b,0x269f1e,0x26a273,0x26a47a,0x26a709,0x26a95e,0x26ac14,0x26af50,0x26b161,0x26b4ac,0x26b7c2,0x26ba6a,0x26be76,0x26c0f3,0x26c204,0x26c356,0x26c510,0x26cd06
      };  
    
    static const std::vector<ADDRINT> dispatchTableLoadAddresses = {
      0x25bc2a,0x25bca1,0x25bd5a,0x25be60,0x25bf3f,0x25c01c,0x25c0f2,0x25c22e,0x25c381,0x25c4cb,0x25c5ff,0x25c754,0x25c842,0x25c8e3,0x25c990,0x25ca3a,0x25cb05,0x25cb9f,0x25cc8c,0x25cd9b,0x25cef0,0x25d03d,0x25d18f,0x25d2e4,0x25d474,0x25d60f,0x25d761,0x25d888,0x25d939,0x25dab7,0x25dcea,0x25deb5,0x25e1f7,0x25e2e4,0x25e404,0x25e4b5,0x25e632,0x25e7a7,0x25e8c7,0x25e9dd,0x25ed99,0x25ef3e,0x25f096,0x25f29a,0x25f4a4,0x25f5b3,0x25f7db,0x25fa7f,0x25fc21,0x25fd76,0x25fe66,0x260017,0x260121,0x26027d,0x2603ac,0x26043a,0x26051c,0x26072d,0x2608db,0x2609f6,0x260b6d,0x260c62,0x260d59,0x260e14,0x260f35,0x2611ff,0x2613e8,0x261508,0x2616ce,0x2617cb,0x261879,0x261923,0x261a45,0x261c2d,0x261d19,0x261e4f,0x261f71,0x26209a,0x2621c3,0x2622d5,0x2623fd,0x262569,0x2626e3,0x262906,0x2629ec,0x262cee,0x262ddb,0x262f2a,0x263049,0x263146,0x263212,0x26331c,0x2634e6,0x263707,0x2638a7,0x2639b4,0x263ae6,0x263d6e,0x264036,0x2641b0,0x2642a5,0x264416,0x2646c8,0x264981,0x264ba4,0x264d23,0x264f48,0x26518a,0x265312,0x26542e,0x26555b,0x2655fb,0x2656b9,0x265775,0x2657dc,0x265870,0x2659b3,0x265afe,0x265b62,0x265bf6,0x265d36,0x265e5f,0x265ef2,0x265fb3,0x26608f,0x26618c,0x2662ab,0x26630f,0x2663a7,0x2664c3,0x266527,0x2665bf,0x2666cf,0x2667e6,0x26695f,0x266adc,0x266bc9,0x266ca7,0x266d73,0x266e38,0x266f34,0x26704d,0x267183,0x26734a,0x26752f,0x267679,0x2677db,0x267936,0x267aa0,0x267cf1,0x267ed8,0x2680ec,0x2682ff,0x268432,0x26858f,0x268641,0x2686e7,0x268a4e,0x268c4c,0x268d62,0x268df6,0x2693ae,0x269570,0x269720,0x2699aa,0x269bd9,0x269f5c,0x26a2b1,0x26a4b8,0x26a747,0x26a99c,0x26ac52,0x26af86,0x26b19f,0x26b4e2,0x26b7fe,0x26baa6,0x26beaf,0x26c124,0x26c235,0x26c393,0x26c4cd,0x26c546,0x26c5ed,0x26c681,0x26c793,0x26cd40
  };

    ADDRINT insAddr = INS_Address(ins) - mainModuleBase;
    if (std::find_if(byteCodeLoadAddresses.begin(), byteCodeLoadAddresses.end(),
        [insAddr](ADDRINT byteCodeLoadAddress) {
            return byteCodeLoadAddress == insAddr;
      }) != byteCodeLoadAddresses.end()) {
          // Start tracing when encountering bytecodes
          if (!startTracing) startTracing = true; 
          INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR) MemoryLoadType, IARG_BOOL, true, IARG_BOOL, false, IARG_END);
      } else if (std::find_if(dispatchTableLoadAddresses.begin(), dispatchTableLoadAddresses.end(),
        [insAddr](ADDRINT byteCodeLoadAddress) {
            return byteCodeLoadAddress == insAddr;
      }) != dispatchTableLoadAddresses.end()) {
          INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR) MemoryLoadType, IARG_BOOL, false, IARG_BOOL, true, IARG_END);
      }
        else {
          INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR) MemoryLoadType, IARG_BOOL, false, IARG_BOOL, false, IARG_END);
      }
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

  // finalize each instruction with this function
  INS_InsertIfCall(ins, IPOINT_BEFORE, (AFUNPTR)ShouldWrite, IARG_END);
  INS_InsertThenCall(ins, IPOINT_BEFORE, (AFUNPTR)WriteCurrentInstruction, IARG_END);
}

/*!
 * Print out analysis results.
 * This function is called when the application exits.
 * @param[in]   code            exit code of the application
 * @param[in]   v               value specified by the tool in the
 *                              PIN_AddFiniFunction function call
 */
VOID Fini(INT32 code, VOID* v) { 
    outfile.close(); 
    debugFile.close();
    std::cout << "\r" << "Seen bytecodes: " << seenBytecodes << std::endl;
    std::cout << "\r" << "Seen dispatch table loads: " << seenTableLoads << std::endl;
    for (ADDRINT wrongByteCodeIns : wrongBytecodes) {
      std::cout << "Loaded 0 " << std::hex << wrongByteCodeIns << "\n";
    }
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

  outfile.open(KnobOutputFile.Value().c_str(), std::ios_base::binary | std::ios_base::trunc);
  debugFile.open(KnobDebugFile.Value().c_str());
  debugFile.setf(std::ios::showbase);
  if (!outfile) {
    std::cout << "Couldn't open output trace file. Exiting." << std::endl;
    exit(1);
  }

  // Fix base adress to enable calculation of offset
  IMG_AddInstrumentFunction(Image, 0);
  
  // Register function to be called to instrument instructions
  INS_AddInstrumentFunction(Instruction, 0);

  // Register function to be called when the application exits
  PIN_AddFiniFunction(Fini, 0);

  // Start the program, never returns
  PIN_StartProgram();

  return 0;
}
