"""
Script kiểm tra 5 API key Groq trong .env và model tương ứng.
Không cần chạy benchmark — chạy script này trước để xác nhận
cơ chế fallback hoạt động đúng.

Dùng:
    python -m backend.tools.check_api_keys

Output:
    - Danh sách key được load theo thứ tự sequential
    - Model sẽ thử trên mỗi key
    - Kết quả test từng key × model
"""
from __future__ import annotations

import os
import sys
import time

# Ensure project root on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from openai import OpenAI


AVAILABLE_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
]

# Same order as APIFallbackManager
DEFAULT_KEY_ORDER = [
    "GROQ_API_KEY",
    "NEW_GROQ_API_KEY",
    "GROQ_API_KEY_1",
    "GROQ_API_KEY_2",
    "GROQ_API_KEY_3",
]


def get_keys_in_order() -> list[tuple[str, str, int]]:
    """Trả về list (env_var, key_value, slot) theo thứ tự sequential."""
    override = os.environ.get("GROQ_KEY_ORDER", "").strip()
    if override:
        order = [n.strip() for n in override.split(",") if n.strip()]
    else:
        order = list(DEFAULT_KEY_ORDER)

    seen: set[str] = set()
    deduped: list[str] = []
    for name in order:
        if name in seen:
            continue
        seen.add(name)
        deduped.append(name)

    keys = []
    slot = 0
    for var in deduped:
        val = os.environ.get(var, "").strip()
        if val:
            keys.append((var, val, slot))
            slot += 1
    return keys


def label_of(env_var: str, slot: int) -> str:
    if env_var == "GROQ_API_KEY":
        return "PRIMARY"
    if env_var == "NEW_GROQ_API_KEY":
        return "BACKUP_NEW"
    if env_var.startswith("GROQ_API_KEY_"):
        return f"KEY_{env_var.split('_')[-1]}"
    return f"KEY_{slot}"


def models_for_slot(slot: int) -> list[str]:
    """Đọc GROQ_KEY_MODELS_<slot> hoặc dùng default."""
    override = os.environ.get(
        f"GROQ_KEY_MODELS_{slot}",
        "",
    ).strip()
    if override:
        return [m.strip() for m in override.split(",") if m.strip()]
    return [m for m, _ in [
        ("openai/gpt-oss-120b", 0),
        ("openai/gpt-oss-20b", 1),
        ("qwen/qwen3.8-27b", 2),
    ]]


def test_key_model(key: str, model: str) -> tuple[bool, str]:
    try:
        client = OpenAI(
            api_key=key,
            base_url="https://api.groq.com/openai/v1",
        )
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say OK in one word."}],
            temperature=0.1,
            max_completion_tokens=10,
        )
        content = (response.choices[0].message.content or "").strip()
        tokens = (
            response.usage.total_tokens
            if response.usage else 0
        )
        return True, f"OK — {content!r} ({tokens} tokens)"
    except Exception as exc:  # noqa: BLE001
        return False, f"FAIL — {type(exc).__name__}: {exc}"


def format_key_preview(key: str) -> str:
    if len(key) <= 8:
        return key[:3] + "..."
    return key[:4] + "..." + key[-4:]


def main() -> None:
    print("=" * 70)
    print("GROQ API Key Checker (sequential fallback)")
    print("=" * 70)

    keys = get_keys_in_order()

    if not keys:
        print("\n[ERROR] Không tìm thấy GROQ_API_KEY nào trong .env.")
        print("\nThêm vào .env (theo thứ tự sequential này):")
        for i, var in enumerate(DEFAULT_KEY_ORDER):
            print(f"  {var} = gsk_xxxx")
        print("\nMỗi key sẽ thử tuần tự 3 model:")
        print(f"  {AVAILABLE_MODELS}")
        return

    print(f"\nTìm thấy {len(keys)} API key theo thứ tự sequential:")
    print()
    for env_var, key_val, slot in keys:
        label = label_of(env_var, slot)
        models = models_for_slot(slot)
        print(
            f"  slot {slot}  {label:<14}  ({format_key_preview(key_val)})"
            f"\n    env: {env_var}"
            f"\n    models (priority order): {models}"
        )

    print()
    print("-" * 70)
    print("Testing connectivity (key × model) ...")
    print("-" * 70)

    all_ok = True
    for env_var, key_val, slot in keys:
        label = label_of(env_var, slot)
        models = models_for_slot(slot)
        print(f"\n[slot {slot}] {label}  ({env_var})")
        for model in models:
            ok, msg = test_key_model(key_val, model)
            status = "[  OK  ]" if ok else "[ FAIL ]"
            print(f"  {status} {model:<30} {msg}")
            if not ok:
                all_ok = False
            time.sleep(1)

    print()
    print("=" * 70)
    if all_ok:
        print("Tất cả key × model đều hoạt động!")
        print("Bạn có thể chạy benchmark với sequential fallback.")
        print()
        print("Thứ tự fallback khi quota hết:")
        for env_var, _, slot in keys:
            label = label_of(env_var, slot)
            print(
                f"  slot {slot}: {label}  "
                f"({len(models_for_slot(slot))} model)"
            )
    else:
        print("Một số key × model thất bại.")
        print("Hệ thống vẫn chạy được nhờ fallback — case bị fail")
        print("sẽ tự động nhảy sang key+model tiếp theo.")
    print("=" * 70)


if __name__ == "__main__":
    main()