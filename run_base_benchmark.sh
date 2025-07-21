./install_local.sh

NUM_EXPERIMENTS=${1:-1}

python benchmarks/base_benchmark.py --num-experiments $NUM_EXPERIMENTS