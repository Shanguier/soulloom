#!/usr/bin/env python3
"""
SoulLoom — Stage Analyzer
Time distribution analysis and stage detection for chat dialogue JSON.

Usage:
    python3 stage_analyzer.py <chat.json> [--min-gap DAYS] [--min-messages N]

Output:
    - Message statistics (total, time span, per-participant)
    - Time distribution (daily/weekly/monthly)
    - Auto-detected stages with dynamic naming suggestions
"""

import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict


def load_chat(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Support both formats: list of messages or {name, other_name, dates} wrapper
    if isinstance(data, dict):
        if "dates" in data:
            # wx-export format: {name, other_name, self_name, dates: [{d, msgs}]}
            messages = []
            self_name = data.get("self_name", "我")
            other_name = data.get("other_name", data.get("name", "对方"))
            for day in data["dates"]:
                date_str = day["d"]
                for msg in day["msgs"]:
                    sender = self_name if msg.get("s") == 0 else other_name
                    messages.append({
                        "s": sender,
                        "t": f"{date_str} {msg.get('t', '00:00')}",
                        "m": msg.get("m", "")
                    })
            return messages, (self_name, other_name)
        elif "messages" in data:
            messages = data["messages"]
        else:
            messages = data
    else:
        messages = data

    # Detect participants from data
    senders = set()
    for msg in messages:
        s = msg.get("s", msg.get("sender", ""))
        senders.add(s)

    # Try to determine self vs other
    # If exactly 2 senders, ask user to identify themselves later
    return messages, list(senders)


def parse_time(t_str):
    """Parse flexible time formats."""
    for fmt in [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d",
    ]:
        try:
            return datetime.strptime(t_str.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def parse_date(d_str):
    for fmt in ["%Y-%m-%d", "%Y/%m/%d"]:
        try:
            return datetime.strptime(d_str.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def analyze(messages):
    """Main analysis: stats, distribution, stage detection."""
    # Parse all messages
    parsed = []
    for msg in messages:
        t_str = msg.get("t", msg.get("time", msg.get("timestamp", "")))
        dt = parse_time(t_str)
        if dt:
            parsed.append({
                "sender": msg.get("s", msg.get("sender", "未知")),
                "text": msg.get("m", msg.get("message", msg.get("text", ""))),
                "datetime": dt,
                "date": dt.date(),
            })

    if not parsed:
        print("❌ No messages could be parsed. Check time format.")
        return

    # Sort by time
    parsed.sort(key=lambda x: x["datetime"])

    # Basic stats
    total = len(parsed)
    start = parsed[0]["datetime"]
    end = parsed[-1]["datetime"]
    span_days = (end - start).days

    sender_counts = defaultdict(int)
    for p in parsed:
        sender_counts[p["sender"]] += 1

    print(f"{'='*50}")
    print(f"📊 Data Overview")
    print(f"{'='*50}")
    print(f"  Total messages : {total}")
    print(f"  Time span      : {start.date()} ~ {end.date()} ({span_days} days)")
    print(f"  Participants   : {', '.join(f'{k} ({v} msgs)' for k, v in sorted(sender_counts.items(), key=lambda x: -x[1]))}")
    print()

    # Daily distribution
    daily = defaultdict(int)
    for p in parsed:
        daily[p["date"]] += 1

    # Weekly distribution
    weekly = defaultdict(int)
    for p in parsed:
        week_start = p["datetime"] - timedelta(days=p["datetime"].weekday())
        weekly[week_start.date()] += 1

    # Monthly distribution
    monthly = defaultdict(int)
    for p in parsed:
        month_key = p["datetime"].strftime("%Y-%m")
        monthly[month_key] += 1

    # Print monthly stats
    print(f"{'='*50}")
    print(f"📅 Monthly Distribution")
    print(f"{'='*50}")
    for month in sorted(monthly.keys()):
        count = monthly[month]
        bar = "█" * min(count // 10, 50)
        print(f"  {month} : {count:5d} {bar}")
    print()

    # Find gaps (consecutive days with 0 messages)
    all_dates = sorted(daily.keys())
    gaps = []
    gap_start = None
    for i in range(1, len(all_dates)):
        diff = (all_dates[i] - all_dates[i - 1]).days
        if diff > 3:
            gaps.append((all_dates[i - 1], all_dates[i], diff))

    if gaps:
        print(f"{'='*50}")
        print(f"⏸️  Notable Gaps (>3 days)")
        print(f"{'='*50}")
        for g in gaps:
            print(f"  {g[0]} ~ {g[1]}  ({g[2]} days)")
        print()

    # Auto stage detection based on volume changes
    mean_daily = total / max(span_days, 1)

    # Smooth volume: 7-day rolling average
    sorted_dates = all_dates
    smooth = {}
    for i, d in enumerate(sorted_dates):
        window_start = max(0, i - 3)
        window_end = min(len(sorted_dates), i + 4)
        window = [daily[sorted_dates[j]] for j in range(window_start, window_end)]
        smooth[d] = sum(window) / len(window)

    # Find stage boundaries: where smoothed volume crosses thresholds
    stages = []
    stage_start = sorted_dates[0]
    stage_avg = smooth[stage_start]
    stage_peak = smooth[stage_start]

    THRESH_HIGH = mean_daily * 1.3
    THRESH_LOW = mean_daily * 0.4

    for d in sorted_dates[1:]:
        v = smooth[d]
        v_prev = smooth[sorted_dates[sorted_dates.index(d) - 1]]

        # Detect significant change
        if (v_prev <= THRESH_LOW and v > THRESH_LOW) or \
           (v_prev >= THRESH_HIGH and v < THRESH_HIGH) or \
           (v_prev <= mean_daily and v > mean_daily and v > v_prev * 2):
            stages.append((stage_start, sorted_dates[sorted_dates.index(d) - 1], stage_avg, stage_peak))
            stage_start = d
            stage_avg = 0
            stage_peak = 0

        stage_avg = (stage_avg + v) / 2
        stage_peak = max(stage_peak, v)

    # Last stage
    if stage_start < sorted_dates[-1]:
        stages.append((stage_start, sorted_dates[-1], stage_avg, stage_peak))

    print(f"{'='*50}")
    print(f"🔍 Detected Stages (based on message volume)")
    print(f"{'='*50}")
    print(f"  Thresholds: High > {THRESH_HIGH:.1f}/day, Low < {THRESH_LOW:.1f}/day")
    print(f"  Mean: {mean_daily:.1f} messages/day")
    print()

    # Name stages based on volume characteristics
    stage_names = []
    for i, (s, e, avg, peak) in enumerate(stages):
        duration = (e - s).days
        total_msgs = sum(daily.get(d, 0) for d in sorted_dates if s <= d <= e)

        # Volume-based classification
        vol_ratio = avg / mean_daily
        if vol_ratio > 1.3:
            vol_type = "high"
        elif vol_ratio < 0.5:
            vol_type = "low"
        else:
            vol_type = "medium"

        print(f"  Stage {i+1}: {s} ~ {e} ({duration} days, {total_msgs} msgs)")
        print(f"    Volume: {vol_type} (avg {avg:.1f}/day, peak {peak:.1f}/day)")
        print()

    print(f"{'='*50}")
    print(f"💡 Next Step")
    print(f"{'='*50}")
    print(f"  Review the stages above and run content analysis to name each stage")
    print(f"  based on WHAT was discussed, not just HOW MUCH.")
    print()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 stage_analyzer.py <chat.json>")
        sys.exit(1)

    path = sys.argv[1]
    messages, participants = load_chat(path)
    print(f"ℹ️  Loaded {len(messages)} messages from {path}")
    print(f"ℹ️  Detected participants: {', '.join(participants)}")
    print()
    analyze(messages)


if __name__ == "__main__":
    main()
