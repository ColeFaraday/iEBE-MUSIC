#!/usr/bin/env python3
"""
Count the number of EVENT_RESULTS_* folders in all event_* subdirectories of a given root folder.
Usage: python count_events.py /path/to/root_folder
"""
import sys
import os

def count_event_results(root_folder):
    total_count = 0
    event_counts = {}
    event_numbers = []
    for entry in os.listdir(root_folder):
        event_path = os.path.join(root_folder, entry)
        if os.path.isdir(event_path) and entry.startswith("event_"):
            try:
                event_num = int(entry.split("_")[1])
                event_numbers.append(event_num)
            except (IndexError, ValueError):
                pass
            count = 0
            for subentry in os.listdir(event_path):
                sub_path = os.path.join(event_path, subentry)
                if os.path.isdir(sub_path) and subentry.startswith("EVENT_RESULTS_"):
                    count += 1
            print(f"{entry}: {count} EVENT_RESULTS folders")
            total_count += count
            event_counts[entry] = count
    print(f"\nTotal EVENT_RESULTS folders: {total_count}")
    if event_counts:
        min_count = min(event_counts.values())
        max_count = max(event_counts.values())
        min_events = [k for k, v in event_counts.items() if v == min_count]
        max_events = [k for k, v in event_counts.items() if v == max_count]
        print(f"Min EVENT_RESULTS count: {min_count} in {', '.join(min_events)}")
        print(f"Max EVENT_RESULTS count: {max_count} in {', '.join(max_events)}")
    else:
        print("No event folders found.")

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} /path/to/root_folder")
        sys.exit(1)
    root_folder = sys.argv[1]
    if not os.path.isdir(root_folder):
        print(f"Error: {root_folder} is not a valid directory.")
        sys.exit(1)
    count_event_results(root_folder)

if __name__ == "__main__":
    main()
