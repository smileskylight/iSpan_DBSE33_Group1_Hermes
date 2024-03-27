## step 1 import packages ##
from datasets import Dataset, load_dataset, concatenate_datasets
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    DataCollatorForSeq2Seq,
    TrainingArguments,
    Trainer,
)
import os
from transformers.trainer_callback import TrainerState
from peft import PeftModel
from torch.utils.data import DataLoader

## step 2 load dataset ##
ds = load_dataset("erhwenkuo/alpaca-data-gpt4-chinese-zhtw", split="train")

ds_travel_set1 = load_dataset(
    "json", data_files="./travel_advisor_output_v1.json", split="train"
)

ds_travel_set2 = load_dataset(
    "json", data_files="./travel_advisor_output_v2.json", split="train"
)

ds_travel_set3 = load_dataset(
    "json", data_files="./travel_advisor_output_v3.json", split="train"
)

# Combine the datasets
combined_dataset = concatenate_datasets(
    [ds_travel_set1, ds_travel_set2, ds_travel_set3]
)

## step 3 dataset preprocess ##
# choose model
tokenizer = AutoTokenizer.from_pretrained("yentinglin/Taiwan-LLM-7B-v2.1-chat")

tokenizer.padding_side = (
    "right"  # padding_side must be right 否則 batch 大於 1 時可能不收斂
)
tokenizer.pad_token_id = 2

# Specify the index or indices you want to remove
indices_to_remove = {1339}  # This could be a set for efficiency

# Filter out the specified indices
filtered_dataset = combined_dataset.filter(
    lambda example, indice: indice not in indices_to_remove, with_indices=True
)

# Now, filtered_dataset doesn't contain the entries from indices_to_remove


# build in dataset
def process_func(example):
    MAX_LENGTH = 384  # Llama 分詞會把一個中文字切分成多個 token 因此需要放開一些最大長度 保持數據完整性
    input_ids, attention_mask, labels = [], [], []
    instruction = tokenizer(
        "\n".join(["Human: " + example["question"], example["input"]]).strip()
        + "\n\nAssistant: ",
        add_special_tokens=False,
    )
    response = tokenizer(example["output"], add_special_tokens=False)
    input_ids = (
        instruction["input_ids"] + response["input_ids"] + [tokenizer.eos_token_id]
    )
    attention_mask = instruction["attention_mask"] + response["attention_mask"] + [1]
    labels = (
        [-100] * len(instruction["input_ids"])
        + response["input_ids"]
        + [tokenizer.eos_token_id]
    )
    if len(input_ids) > MAX_LENGTH:
        input_ids = input_ids[:MAX_LENGTH]
        attention_mask = attention_mask[:MAX_LENGTH]
        labels = labels[:MAX_LENGTH]
    return {"input_ids": input_ids, "attention_mask": attention_mask, "labels": labels}


# tokenized_ds = combined_dataset.map(process_func, remove_columns=combined_dataset.column_names)
tokenized_ds = filtered_dataset.map(
    process_func, remove_columns=filtered_dataset.column_names
)

## step 4 build model ##
save_dir = r".\chatbot"
ckpt_dirs = os.listdir(save_dir)

if "runs" in ckpt_dirs:
    ckpt_dirs.remove("runs")
    ckpt_dirs = sorted(ckpt_dirs, key=lambda x: int(x.split("-")[1]))

last_ckpt = ckpt_dirs[-1]

state = TrainerState.load_from_json(f"{save_dir}/{last_ckpt}/trainer_state.json")

print(state)  # your best ckpoint

# cloud authentication
from huggingface_hub import notebook_login

notebook_login()

# Load your model
model = AutoModelForCausalLM.from_pretrained("yentinglin/Taiwan-LLM-7B-v2.1-chat")

# check
print(model.dtype)

#################################################
### Lora
#################################################

## PEFT step 1 setup the data document ##
from peft import LoraConfig, TaskType, get_peft_model

config = LoraConfig(task_type=TaskType.CAUSAL_LM)

## PEFT step 2 build model
model = get_peft_model(model, config)
model.enable_input_require_grads()  # 開啟梯度檢查點
model = model.half()  # 若模型為 fp16 時 需要將adam_epsilon 調大
model.print_trainable_parameters()

dl = DataLoader(
    tokenized_ds,
    batch_size=2,
    collate_fn=DataCollatorForSeq2Seq(tokenizer=tokenizer, padding=True),
)
ipt = next(enumerate(dl))[1]
model.to("cuda")
model(**ipt.to("cuda"))

## PEFT step 5 set training parameters ##
args = TrainingArguments(
    output_dir="./chatbot",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    gradient_checkpointing=True,
    logging_steps=5,
    num_train_epochs=5,
    save_steps=20,
    adam_epsilon=1e-3,
)

## PEFT step 6 set trainer ##
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_ds,
    data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer, padding=True),
)

## PEFT step 7 train model ##
trainer.train()

## PEFT step 8 model inference ##
model.eval()
ipt = tokenizer(
    "Human: {}\n{}".format(
        "我想在澎湖尋找一些適合親子活動的地方，有推薦嗎？", ""
    ).strip()
    + "\n\nAssistant: ",
    return_tensors="pt",
).to(model.device)
tokenizer.decode(
    model.generate(
        **ipt, max_length=512, do_sample=True, eos_token_id=tokenizer.eos_token_id
    )[0],
    skip_special_tokens=True,
)
