given following cli format, write a python wrapper that support -h, -f (audio-path) 

usage: ./main [options] file0.wav file1.wav ...

options:
  -h,        --help              [default] show this help message and exit
  -t N,      --threads N         [4      ] number of threads to use during computation
  -p N,      --processors N      [1      ] number of processors to use during computation
  -et N,     --entropy-thold N   [2.40   ] entropy threshold for decoder fail
  -lpt N,    --logprob-thold N   [-1.00  ] log probability threshold for decoder fail
  -otxt,     --output-txt        [false  ] output result in a text file
  -oj,       --output-json       [false  ] output result in a JSON file
  -of FNAME, --output-file FNAME [       ] output file path (without file extension)


given attached example of calling ollama + mistral (query-paper-ollama.py), I want to have a similar code solution to summarize above audio-to-text results. 

