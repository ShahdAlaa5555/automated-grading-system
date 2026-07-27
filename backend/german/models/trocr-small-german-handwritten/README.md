---
license: afl-3.0
datasets:
- fhswf/german_handwriting
language:
- de
metrics:
- cer
base_model:
- microsoft/trocr-small-handwritten
---

# EpsilonGreedy/TrOCR_small_german_handwritten

This is a small 250mio german handwriting ocr model. <br>
It works best on images of coherent lines or phrases of text. <br>
Does not work on multiline images. <br>
You can find training and eval metrics in the metrics tab <br> <br>

Only evaluated: CER of around 4.4% <br>
You can find the big brother over here (https://huggingface.co/fhswf/TrOCR_german_handwritten)
which has CER 4.1% and WER of 17.5%. So WER will be analogous.

Thanks to Fachhochschule Südwestfalen
(https://huggingface.co/fhswf) for the great dataset (https://huggingface.co/datasets/fhswf/german_handwriting).
Further thanks to:<br>
Microsoft for the base model.<br>
Google for letting me train on kaggle for free! (https://www.kaggle.com/code/treeinsight/trocr-german-small-finetune)<br>
Huggingface for hosting this model. 

