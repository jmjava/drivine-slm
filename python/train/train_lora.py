from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from drivine_lab.paths import INSTRUCT_PATH, PROFILES_PATH, REPO_ROOT


SYSTEM_PROMPT = (
    "You are a local assistant specialized in Drivine, the multi-language graph "
    "database client (TypeScript, Python, JVM). Prefer object-manager views and "
    "the typed DSL; use PersistenceManager Cypher when needed. Be precise and "
    "include minimal runnable snippets."
)


def _load_profile(profile_id: str) -> dict:
    profiles = json.loads(Path(PROFILES_PATH).read_text(encoding="utf-8"))
    for p in profiles:
        if p["id"] == profile_id:
            return p
    raise SystemExit(f"Unknown profile '{profile_id}'. See data/amd_profiles.json")


def _load_rows(path: Path) -> list[dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [{"instruction": r["instruction"], "response": r["response"]} for r in raw]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="LoRA SFT on the Drivine instruction dataset (AMD ROCm friendly).")
    parser.add_argument("--profile", default="geekom-a9-mega", help="AMD profile id from data/amd_profiles.json")
    parser.add_argument("--model", default=None, help="Override base instruct model")
    parser.add_argument("--data", default=str(INSTRUCT_PATH))
    parser.add_argument("--output", default=str(REPO_ROOT / "outputs" / "drivine-lora"))
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--lora-r", type=int, default=None)
    parser.add_argument("--lora-alpha", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--grad-accum", type=int, default=None)
    parser.add_argument("--lr", type=float, default=None)
    parser.add_argument("--max-seq-len", type=int, default=None)
    parser.add_argument("--cpu", action="store_true", help="Force CPU (smoke test without GPU).")
    args = parser.parse_args(argv)

    profile = _load_profile(args.profile)
    cfg = dict(profile["defaultTrain"])
    if args.model:
        cfg["model"] = args.model
    if args.max_steps is not None:
        cfg["maxSteps"] = args.max_steps
    if args.lora_r is not None:
        cfg["loraR"] = args.lora_r
    if args.lora_alpha is not None:
        cfg["loraAlpha"] = args.lora_alpha
    if args.batch_size is not None:
        cfg["batchSize"] = args.batch_size
    if args.grad_accum is not None:
        cfg["gradAccum"] = args.grad_accum
    if args.lr is not None:
        cfg["lr"] = args.lr
    if args.max_seq_len is not None:
        cfg["maxSeqLen"] = args.max_seq_len

    # Import heavy deps only when training actually starts.
    import torch
    from datasets import Dataset
    from peft import LoraConfig, TaskType, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from trl import SFTConfig, SFTTrainer

    rows = _load_rows(Path(args.data))
    print(f"Loaded {len(rows)} instruction pairs from {args.data}")
    print(f"Profile {profile['name']} ({profile['gfx']}) → model {cfg['model']}")

    use_cuda = torch.cuda.is_available() and not args.cpu
    if not use_cuda:
        print("WARNING: training on CPU. On GEEKOM, install ROCm PyTorch for your gfx target.")

    tokenizer = AutoTokenizer.from_pretrained(cfg["model"], trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.model_max_length = int(cfg["maxSeqLen"])

    dtype = torch.bfloat16 if use_cuda and torch.cuda.is_bf16_supported() else torch.float32
    model_kwargs: dict = {
        "trust_remote_code": True,
        "torch_dtype": dtype,
    }
    if use_cuda:
        model_kwargs["device_map"] = "auto"

    # Optional 4-bit path — only if bitsandbytes imports cleanly on this ROCm build.
    quant = None
    if use_cuda and os.environ.get("DRIVINE_QLORA", "").lower() in {"1", "true", "yes"}:
        try:
            quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=dtype)
            model_kwargs["quantization_config"] = quant
            print("QLoRA: 4-bit load enabled via DRIVINE_QLORA=1")
        except Exception as exc:  # pragma: no cover
            print(f"QLoRA requested but bitsandbytes failed ({exc}); continuing with LoRA.")

    model = AutoModelForCausalLM.from_pretrained(cfg["model"], **model_kwargs)
    model.config.use_cache = False
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()

    lora = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=int(cfg["loraR"]),
        lora_alpha=int(cfg["loraAlpha"]),
        lora_dropout=0.05,
        bias="none",
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    def to_text(example: dict) -> dict:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": example["instruction"]},
            {"role": "assistant", "content": example["response"]},
        ]
        if hasattr(tokenizer, "apply_chat_template"):
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        else:
            text = (
                f"System: {SYSTEM_PROMPT}\n"
                f"User: {example['instruction']}\n"
                f"Assistant: {example['response']}"
            )
        return {"text": text}

    ds = Dataset.from_list(rows).map(to_text)

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    train_args = SFTConfig(
        output_dir=str(out),
        per_device_train_batch_size=int(cfg["batchSize"]),
        gradient_accumulation_steps=int(cfg["gradAccum"]),
        learning_rate=float(cfg["lr"]),
        max_steps=int(cfg["maxSteps"]),
        logging_steps=5,
        save_steps=max(10, int(cfg["maxSteps"]) // 2),
        bf16=bool(use_cuda and dtype == torch.bfloat16),
        fp16=False,
        optim="adamw_torch",
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        report_to="none",
        dataset_text_field="text",
        max_length=int(cfg["maxSeqLen"]),
        packing=False,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
    )

    trainer = SFTTrainer(
        model=model,
        args=train_args,
        train_dataset=ds,
        processing_class=tokenizer,
    )

    stats = trainer.train()
    trainer.save_model(str(out))
    tokenizer.save_pretrained(str(out))
    (out / "train_summary.json").write_text(
        json.dumps({"profile": profile["id"], "config": cfg, "metrics": stats.metrics}, indent=2),
        encoding="utf-8",
    )
    print(f"Saved LoRA adapter to {out}")


if __name__ == "__main__":
    main()
