# WWPNAI
Code used for the Master thesis "Effective Microarchitectural Support for Interpreted Languages" in Electronic System Design and Innovation  

## Relevant folders and files
1. The ChampSim directory contains the ChampSim repository:
    1.  src/ contains the source files for the BB, HDBT and the overall bytecode_module.
    2. inc/ contains the header files. The **bytecode_module** is the overall one.
    3. tracer/ contains the source file for the tracing tool. One has to install Pin to be able to use it

2. The CPython directory contains the source file for our configured CPython implementation and PythonBin contains the binary used in tracing the benchmarks
3. benchmarks/ contains the pure python benchmarks
4. vSwarm includes the vSwarm repository. The benchmarks generate as well as the relevant dockerfiles are found in the benchmarks/video-analytics folder 
5. tools/ contains shell scripts and plotting scripts used to generate the results

