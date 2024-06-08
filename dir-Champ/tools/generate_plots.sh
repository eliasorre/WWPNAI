cd /home/elias/Master/ChampSim

mkdir -p tools/script
mkdir -p tools/script/plots
mkdir -p tools/script/csv

python tools/parse_logs.py logs/bb_size tools/script/csv/bb_size.csv true   
python tools/parse_logs.py logs/baseline_500m tools/script/csv/baselines_500m.csv        
python tools/parse_logs.py logs/baseline_100m tools/script/csv/baselines_100m.csv        
python tools/parse_logs.py logs/hdbt_dbtb_size tools/script/csv/hdbt_size.csv true
python tools/parse_logs.py logs/btb_size tools/script/csv/btb_size.csv true


python3 tools/plot_performance_bb.py tools/script/csv/bb_size.csv  tools/script/plots/performance_bb_python tools/script/plots/performance_bb_native

python3 tools/plot_performance_hdbt.py  tools/script/csv/hdbt_size.csv  tools/script/plots/performance_hdbt_python tools/script/plots/performance_hdbt_native

python3 tools/plot_cache_stats.py  tools/script/csv/baselines_500m.csv  tools/script/plots/cache_stats                 

python3 tools/plotting_performance.py tools/script/csv/baselines_500m.csv tools/script/plots/baseline_python tools/script/plots/baseline_native tools/script/plots/ideal tools/script/plots/minimal  

python3 tools/plot_branch_stats.py tools/script/csv/baselines_500m.csv tools/script/plots/branch_python tools/script/plots/branch_native 

python3 tools/plot_components_hit_stats.py tools/script/csv/baselines_500m.csv  tools/script/plots/bfm_hit_rate 

python3 tools/plot_btb_experiments.py  tools/script/csv/btb_size.csv tools/script/csv/baselines_100m.csv tools/script/plots/btb_python tools/script/plots/btb_native tools/script/plots/btb_indirect 