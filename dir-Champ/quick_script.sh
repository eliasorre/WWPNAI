bin/champsim --warmup_instructions 20000000 --simulation_instructions 100000000 --bytecode --json json/decoder2_no_skip $TRACES_ROOT/decoder_thread.2.trace >> logs/decoder_thread_2_no_skip_100m

bin/champsim_skip --warmup_instructions 20000000 --simulation_instructions 100000000 --bytecode --json json/decoder2_skip $TRACES_ROOT/decoder_thread.2.trace >> logs/decoder_thread_2_skip_100m

bin/champsim --warmup_instructions 20000000 --simulation_instructions 100000000 --bytecode --json json/test $TRACES_ROOT/recog_thread.trace >> logs/recog_thread_no_skip_100m

bin/champsim --warmup_instructions 20000000 --simulation_instructions 100000000 --bytecode --json json/test $TRACES_ROOT/recog_thread.trace >> logs/recog_thread_skip_100m
