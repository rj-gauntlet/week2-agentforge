import os
import json
import glob
from datetime import datetime

def generate_report():
    results_dir = os.path.join(os.path.dirname(__file__), "..", "data", "eval_results")
    files = glob.glob(os.path.join(results_dir, "eval_*.json"))
    
    if not files:
        print("No evaluation results found.")
        return

    # Sort files by creation/run time
    files.sort()

    print("# Evaluation Results Report\n")
    print("| Date             | Total | Passed | Pass Rate       | Happy Path      | Multi-Step      | Edge Case       | Adversarial     |")
    print("|------------------|-------|--------|-----------------|-----------------|-----------------|-----------------|-----------------|")

    prev_pass_rate = None
    prev_happy = None
    prev_multi = None
    prev_edge = None
    prev_adv = None

    for fpath in files:
        with open(fpath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue
            
            run_at = data.get("run_at", "")
            try:
                date_str = datetime.strptime(run_at, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M")
            except ValueError:
                try:
                    date_str = datetime.strptime(run_at, "%Y-%m-%dT%H-%M-%SZ").strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    date_str = run_at[:16]

            total = data.get("total", 0)
            passed = data.get("passed", 0)
            pass_rate = data.get("pass_rate_pct", 0.0)
            
            by_cat = data.get("by_category", {})
            happy = by_cat.get("happy_path", {}).get("pass_rate_pct", 0.0)
            multi = by_cat.get("multi_step", {}).get("pass_rate_pct", 0.0)
            edge = by_cat.get("edge_case", {}).get("pass_rate_pct", 0.0)
            adv = by_cat.get("adversarial", {}).get("pass_rate_pct", 0.0)

            def format_val(curr, prev):
                if prev is None or curr == prev:
                    return f"{curr:.1f}%"
                diff = curr - prev
                sign = "+" if diff > 0 else ""
                return f"{curr:.1f}% ({sign}{diff:.1f}%)"

            pass_str = format_val(pass_rate, prev_pass_rate)
            happy_str = format_val(happy, prev_happy)
            multi_str = format_val(multi, prev_multi)
            edge_str = format_val(edge, prev_edge)
            adv_str = format_val(adv, prev_adv)

            print(f"| {date_str:<16} | {total:<5} | {passed:<6} | {pass_str:>15} | {happy_str:>15} | {multi_str:>15} | {edge_str:>15} | {adv_str:>15} |")

            prev_pass_rate = pass_rate
            prev_happy = happy
            prev_multi = multi
            prev_edge = edge
            prev_adv = adv

    # --- Print latest failures ---
    if files:
        latest_file = files[-1]
        with open(latest_file, "r", encoding="utf-8") as f:
            try:
                latest_data = json.load(f)
                failures = [res for res in latest_data.get("results", []) if not res.get("passed", True)]
                
                if failures:
                    print("\n### Latest Failures\n")
                    for fail in failures:
                        print(json.dumps(fail, indent=2))
            except Exception:
                pass

    # --- Save to Markdown file ---
    report_path = os.path.join(results_dir, "..", "EVAL_REPORT.md")
    try:
        # We'll just re-run the logic but redirect to a file.
        with open(report_path, "w", encoding="utf-8") as out:
            out.write("# Evaluation Results Report\n\n")
            out.write("| Date             | Total | Passed | Pass Rate       | Happy Path      | Multi-Step      | Edge Case       | Adversarial     |\n")
            out.write("|------------------|-------|--------|-----------------|-----------------|-----------------|-----------------|-----------------|\n")
            
            prev_pass_rate = None
            prev_happy = None
            prev_multi = None
            prev_edge = None
            prev_adv = None

            for fpath in files:
                with open(fpath, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        continue
                    
                    run_at = data.get("run_at", "")
                    try:
                        date_str = datetime.strptime(run_at, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M")
                    except ValueError:
                        try:
                            date_str = datetime.strptime(run_at, "%Y-%m-%dT%H-%M-%SZ").strftime("%Y-%m-%d %H:%M")
                        except ValueError:
                            date_str = run_at[:16]

                    total = data.get("total", 0)
                    passed = data.get("passed", 0)
                    pass_rate = data.get("pass_rate_pct", 0.0)
                    by_cat = data.get("by_category", {})
                    happy = by_cat.get("happy_path", {}).get("pass_rate_pct", 0.0)
                    multi = by_cat.get("multi_step", {}).get("pass_rate_pct", 0.0)
                    edge = by_cat.get("edge_case", {}).get("pass_rate_pct", 0.0)
                    adv = by_cat.get("adversarial", {}).get("pass_rate_pct", 0.0)

                    def format_val(curr, prev):
                        if prev is None or curr == prev:
                            return f"{curr:.1f}%"
                        diff = curr - prev
                        sign = "+" if diff > 0 else ""
                        return f"{curr:.1f}% ({sign}{diff:.1f}%)"

                    pass_str = format_val(pass_rate, prev_pass_rate)
                    happy_str = format_val(happy, prev_happy)
                    multi_str = format_val(multi, prev_multi)
                    edge_str = format_val(edge, prev_edge)
                    adv_str = format_val(adv, prev_adv)

                    out.write(f"| {date_str:<16} | {total:<5} | {passed:<6} | {pass_str:>15} | {happy_str:>15} | {multi_str:>15} | {edge_str:>15} | {adv_str:>15} |\n")

                    prev_pass_rate = pass_rate
                    prev_happy = happy
                    prev_multi = multi
                    prev_edge = edge
                    prev_adv = adv

            if failures:
                out.write("\n### Latest Failures\n\n")
                for fail in failures:
                    out.write(f"```json\n{json.dumps(fail, indent=2)}\n```\n\n")

    except Exception as e:
        print(f"\nCould not save EVAL_REPORT.md: {e}")

if __name__ == "__main__":
    generate_report()
