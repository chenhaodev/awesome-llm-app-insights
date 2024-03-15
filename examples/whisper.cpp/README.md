Download model per [distilled-models](docs/distilled-models.md)

```bash
# clone OpenAI whisper and whisper.cpp
git clone https://github.com/openai/whisper
git clone https://github.com/ggerganov/whisper.cpp

# get the models
cd whisper.cpp/models
git clone https://huggingface.co/distil-whisper/distil-medium.en
git clone https://huggingface.co/distil-whisper/distil-large-v2

# convert to ggml
python3 ./convert-h5-to-ggml.py ./distil-medium.en/ ../../whisper .
mv ggml-model.bin ggml-medium.en-distil.bin

python3 ./convert-h5-to-ggml.py ./distil-large-v2/ ../../whisper .
mv ggml-model.bin ggml-large-v2-distil.bin
```

Config whisper.cpp per [whisper-install](docs/whisper-install.md)

```bash
# build the main example
make

# transcribe an audio file
./main -f samples/jfk.wav
```

Run demo

```bash
python src/whisper-cli.py -f samples/jfk.wav
python src/mistral-cli.py -t <above-text-from-wav>
python tests/test.py
```
