
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YAML to Mermaid Diagram Converter

このスクリプトは、YAML形式で定義された状態機械（FSM: Finite State Machine）を
Mermaidの状態図（stateDiagram-v2）に変換するツールです。

主な機能:
- YAMLファイルから状態機械の定義を読み込み
- プレースホルダー（{{変数名}}）の解決
- 状態間の遷移条件の詳細なラベル生成
- Mermaid形式の状態図ファイルを出力

使用方法:
    python yaml_to_mermaid.py [yaml_file] [--outdir <output_directory>]

引数:
    yaml_file: 変換するYAMLファイルのパス（省略時はtraining_phases_spec.yaml）
    --outdir: 出力ディレクトリ（省略時は現在のディレクトリ）

出力:
    各フェーズごとに<project_name>_<phase_name>.mmdファイルを生成

YAMLファイルの構造例:
    project:
        name: "example_project"
    globals:
        policies:
            cs_minus_abort_penalty_sec: 5.0
    phases:
        - name: "phase1"
          fsm:
            states:
              - name: "ITI"
                transitions:
                  - to: "Trial"
                    after_sec: 2.0
              - name: "Trial"
                transitions:
                  - to: "ITI"
                    guard_all:
                      - type: "speed_below"
                        threshold: 1.0
                        duration_sec: 3.0
                    prob: 0.8

プレースホルダー機能:
    YAML内で{{globals.policies.cs_minus_abort_penalty_sec}}のような形式で
    グローバル変数を参照できます。

ガード条件のサポート:
    - speed_below: 速度が閾値以下
    - no_lick: リックなし
    - mean_speed_below: 平均速度が閾値以下
    - speed_above: 速度が閾値以上
"""

import sys, os, re, argparse, copy
from typing import Any, Dict, List
import yaml

def deep_merge(a: dict, b: dict) -> dict:
    out = copy.deepcopy(a)
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out

_placeholder_re = re.compile(r"\{\{\s*([^}]+?)\s*\}\}")

def resolve_path(ctx: dict, path: str):
    parts = path.split(".")
    cur = ctx
    for p in parts:
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            raise KeyError(f"Unknown placeholder path: {path}")
    return cur

def resolve_placeholders(obj, ctx):
    if isinstance(obj, str):
        def repl(m):
            key = m.group(1)
            val = resolve_path(ctx, key)
            return str(val)
        return _placeholder_re.sub(repl, obj)
    elif isinstance(obj, list):
        return [resolve_placeholders(x, ctx) for x in obj]
    elif isinstance(obj, dict):
        return {k: resolve_placeholders(v, ctx) for k, v in obj.items()}
    else:
        return obj

def format_guard(g: Dict[str, Any]) -> str:
    t = g.get("type")
    if t == "speed_below":
        return f"v<{g.get('threshold')} cm/s for {g.get('duration_sec')} s"
    if t == "no_lick":
        return f"no-lick {g.get('duration_sec')} s"
    if t == "mean_speed_below":
        return f"mean v(last {g.get('window_sec')} s) < {g.get('threshold')} cm/s"
    if t == "speed_above":
        return f"v>{g.get('threshold')} cm/s for {g.get('duration_sec')} s"
    parts = []
    for k,v in g.items():
        if k != "type":
            parts.append(f"{k}={v}")
    return f"{t}({', '.join(parts)})" if t else ", ".join(parts)

def label_for_transition(tr: Dict[str, Any], ctx: Dict[str, Any]) -> str:
    segs = []
    if "after_range_sec" in tr:
        r = tr["after_range_sec"]
        segs.append(f"t∈[{r.get('min')}–{r.get('max')}] s")
    if "after_sec" in tr:
        segs.append(f"after {tr['after_sec']} s")
    if "guard_all" in tr:
        segs.extend([format_guard(g) for g in tr["guard_all"]])
    if "prob" in tr:
        segs.append(f"p={tr['prob']}")
    if tr.get("abort"):
        pen = ctx["globals"]["policies"].get("cs_minus_abort_penalty_sec", 0)
        try:
            pen = float(pen)
        except:
            pen = 0.0
        if pen > 0:
            segs.append(f"+ penalty {pen} s")
    if tr.get("else"):
        segs.append("else")
    return (": " + " & ".join(segs)) if segs else ""

def fsm_to_mermaid(fsm: Dict[str, Any], ctx: Dict[str, Any], start_pref: str="ITI") -> str:

    states = fsm.get("states", [])
    names = [s.get("name","STATE") for s in states]
    start = start_pref if start_pref in names else (names[0] if names else "Start")
    lines = ["stateDiagram-v2", f"  [*] --> {start}"]
    for s in states:
        sname = s.get("name","STATE")
        for tr in s.get("transitions", []):
            to = tr.get("to", "STATE")
            label = label_for_transition(tr, ctx)
            lines.append(f"  {sname} --> {to}{label}")
    return "\n".join(lines) + "\n"

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("yaml_path", nargs='?', default="training_phases_spec.yaml", 
                   help="YAML file path (default: training_phases_spec.yaml in current directory)")
    ap.add_argument("--outdir", default=None, help="Output directory (default: current working directory)")
    args = ap.parse_args()

    spec = yaml.safe_load(open(args.yaml_path, "r", encoding="utf-8"))
    proj = spec.get("project", {}).get("name", "project")
    outdir = args.outdir if args.outdir is not None else os.getcwd()
    os.makedirs(outdir, exist_ok=True)

    base_globals = spec.get("globals", {})
    phases = spec.get("phases", [])
    created = []
    for ph in phases:
        name = ph.get("name","phase")
        if ph.get("skip_mmd"):
            continue
        phase_globals = deep_merge(base_globals, ph.get("overrides", {}))
        ctx = {"globals": phase_globals, "phase": ph}

        fsm = copy.deepcopy(ph.get("fsm", {}))
        fsm = resolve_placeholders(fsm, ctx)

        mmd = fsm_to_mermaid(fsm, ctx, start_pref="ITI")
        fn = f"{proj}_{name}.mmd"
        path = os.path.join(outdir, fn)
        with open(path, "w", encoding="utf-8") as f:
            f.write(mmd)
        created.append(os.path.abspath(path))

    print("Created Mermaid files:")
    for p in created:
        print(" -", p)

if __name__ == "__main__":
    main()
