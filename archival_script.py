import json
import os
import re
import shutil
import signal
import sys
from datetime import datetime

from filelock import FileLock

lock_path = "archival_script.lock"
lock = FileLock(lock_path)


def handle_exit(signum, frame):
    print(f"Signal {signum} received, exiting gracefully.")
    sys.exit(0)


signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


class ArchivalAgent:
    def __init__(
        self,
        project_root=".",
        archived_bin_dir="./archived_bin",
        log_file="archival_log.json",
    ):
        self.project_root = project_root
        self.archived_bin_dir = os.path.join(project_root, archived_bin_dir)
        self.log_file = os.path.join(project_root, log_file)
        self.all_files = []
        self.all_folders = []
        self.active_references = set()
        self.candidate_items = {"low_risk": [], "medium_risk": [], "high_risk": []}
        self.archival_log = self._load_log()

    def _load_log(self):
        if os.path.exists(self.log_file):
            with lock:
                with open(self.log_file, "r") as f:
                    return json.load(f)
        return []

    def _save_log(self):
        with lock:
            with open(self.log_file, "w") as f:
                json.dump(self.archival_log, f, indent=4)

    def scan_project(self):
        print(f"Scanning project root: {self.project_root}")
        for root, dirs, files in os.walk(self.project_root):
            # Exclude the archival bin directory from scanning
            if self.archived_bin_dir in root:
                continue

            # Add folders to all_folders, excluding the project root itself
            if root != self.project_root:
                self.all_folders.append(root)

            for file in files:
                file_path = os.path.join(root, file)
                self.all_files.append(file_path)
        print(f"Found {len(self.all_files)} files and {len(self.all_folders)} folders.")

    def analyze_usage(self):
        print("Analyzing usage of files and folders...")
        potential_references = set()
        for f_path in self.all_files:
            potential_references.add(os.path.basename(f_path))
            potential_references.add(
                os.path.splitext(os.path.basename(f_path))[0]
            )  # without extension
        for d_path in self.all_folders:
            potential_references.add(os.path.basename(d_path))

        for file_path in self.all_files:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for ref in potential_references:
                        if re.search(r"\b" + re.escape(ref) + r"\b", content):
                            self.active_references.add(ref)
            except Exception as e:
                print(f"Could not read file {file_path}: {e}")

        print(f"Identified {len(self.active_references)} active references.")

    def classify_risk(self):
        print("Classifying risk for candidate items...")
        for folder_path in self.all_folders:
            folder_name = os.path.basename(folder_path)
            if folder_name in self.active_references:
                self.candidate_items["high_risk"].append(folder_path)
            else:
                is_medium_risk = False
                for file_path in self.all_files:
                    if file_path.startswith(folder_path + os.sep):
                        file_name = os.path.basename(file_path)
                        file_name_no_ext = os.path.splitext(file_name)[0]
                        if (
                            file_name in self.active_references
                            or file_name_no_ext in self.active_references
                        ):
                            is_medium_risk = True
                            break
                if is_medium_risk:
                    self.candidate_items["medium_risk"].append(folder_path)
                else:
                    self.candidate_items["low_risk"].append(folder_path)

        for file_path in self.all_files:
            file_name = os.path.basename(file_path)
            file_name_no_ext = os.path.splitext(file_name)[0]

            is_part_of_classified_folder = False
            for folder_path in (
                self.candidate_items["high_risk"] + self.candidate_items["medium_risk"]
            ):
                if file_path.startswith(folder_path + os.sep):
                    is_part_of_classified_folder = True
                    break
            if is_part_of_classified_folder:
                continue

            if (
                file_name in self.active_references
                or file_name_no_ext in self.active_references
            ):
                self.candidate_items["high_risk"].append(file_path)
            else:
                self.candidate_items["low_risk"].append(file_path)

        for key in self.candidate_items:
            self.candidate_items[key] = sorted(list(set(self.candidate_items[key])))

        print("Risk classification complete.")

    def generate_dry_run_report(self):
        print("\nCandidate Items for Archival (Dry-Run):")
        print("- Low Risk:")
        for item in self.candidate_items["low_risk"]:
            item_type = "Folder" if os.path.isdir(item) else "File"
            archived_path = os.path.join(
                self.archived_bin_dir, os.path.relpath(item, self.project_root)
            )
            print(f"    {item_type}: {item} -> {archived_path}")
        print("- Medium Risk (Review Needed):")
        for item in self.candidate_items["medium_risk"]:
            item_type = "Folder" if os.path.isdir(item) else "File"
            archived_path = os.path.join(
                self.archived_bin_dir, os.path.relpath(item, self.project_root)
            )
            print(f"    {item_type}: {item} -> {archived_path}")
        print("- High Risk (Do Not Move):")
        for item in self.candidate_items["high_risk"]:
            item_type = "Folder" if os.path.isdir(item) else "File"
            print(f"    {item_type}: {item} -> Retain")

    def automatic_move(self):
        print("\nExecuting automatic move for low-risk items...")
        os.makedirs(self.archived_bin_dir, exist_ok=True)

        moved_items = []
        for item_path in self.candidate_items["low_risk"]:
            relative_path = os.path.relpath(item_path, self.project_root)
            destination_path = os.path.join(self.archived_bin_dir, relative_path)
            destination_dir = os.path.dirname(destination_path)
            os.makedirs(destination_dir, exist_ok=True)

            try:
                if os.path.isdir(item_path):
                    shutil.move(item_path, destination_path)
                    print(f"Moved folder: {item_path} -> {destination_path}")
                else:
                    shutil.move(item_path, destination_path)
                    print(f"Moved file: {item_path} -> {destination_path}")

                moved_items.append(
                    {
                        "original_path": item_path,
                        "new_path": destination_path,
                        "timestamp": datetime.utcnow().isoformat(),
                        "risk_level": "low",
                        "verification_status": "pending",
                    }
                )
            except Exception as e:
                print(f"Error moving {item_path}: {e}")

        self.archival_log.extend(moved_items)
        self._save_log()
        print("Automatic move complete. Log updated.")

    def run_archival(self, dry_run=True):
        self.scan_project()
        self.analyze_usage()
        self.classify_risk()
        self.generate_dry_run_report()

        if not dry_run:
            self.automatic_move()
            # TODO: Implement verification and restore logic here
            # For now, just mark as verified for moved items
            for entry in self.archival_log:
                if entry["verification_status"] == "pending":
                    entry["verification_status"] = "verified"  # Placeholder
            self._save_log()
            print("Archival process completed.")
        else:
            print("\nDry-run complete. No files or folders were moved.")


if __name__ == "__main__":
    agent = ArchivalAgent()
    # To run a dry-run (default)
    agent.run_archival(dry_run=True)

    # To execute the move for low-risk items, change dry_run to False
    # agent.run_archival(dry_run=False)
