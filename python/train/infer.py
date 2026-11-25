from __future__ import annotations

import argparse

from train.train_lora import SYSTEM_PROMPT


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run a prompt against a trained Drivine LoRA adapter.")
    parser.add_argument("--adapter", required=True, help="Path to saved PEFT adapter directory")
    parser.add_argument("--base", default=None, help="Base model if adapter config lacks it")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--max-new-tokens", type=int, default=256)
    parser.add_argument("--cpu", action="store_true")
    args = parser.parse_args(argv)

    import torch
    from peft import AutoPeftModelForCausalLM
    from transformers import AutoTokenizer

    use_cuda = torch.cuda.is_available() and not args.cpu
    dtype = torch.bfloat16 if use_cuda and torch.cuda.is_bf16_supported() else torch.float32

    model = AutoPeftModelForCausalLM.from_pretrained(
        args.adapter,
        device_map="auto" if use_cuda else None,
        torch_dtype=dtype,
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(args.adapter, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": args.prompt},
    ]
    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        prompt = f"System: {SYSTEM_PROMPT}\nUser: {args.prompt}\nAssistant:"

    inputs = tokenizer(prompt, return_tensors="pt")
    if use_cuda:
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=True,
            temperature=0.3,
            top_p=0.9,
            pad_token_id=tokenizer.pad_token_id,
        )
    text = tokenizer.decode(out[0], skip_special_tokens=True)
    # Print only the continuation when possible.
    if "Assistant:" in text:
        print(text.split("Assistant:")[-1].strip())
    else:
        print(text)


if __name__ == "__main__":
    main()
