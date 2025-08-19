
# Chainsaw Event Log Scanner

**Chainsaw Event Log Scanner** is a Python-based tool that provides a simple interface to scan Windows Event Logs (EVTX files) using the [Chainsaw](https://github.com/your-chainsaw-link) Sigma rules engine. It allows users to select folders or mounted images, apply Sigma rules, and export results in CSV format.

---

## Features

- Scan folders or mounted images containing EVTX files.
- Automatic detection of subfolders with EVTX files.
- Integration with Chainsaw executable and Sigma rules.
- Custom case naming and timestamped report generation.
- Outputs logs and CSV reports to user-selected directories.
- Windows GUI file and folder selection dialogs.

---

## Requirements

- Windows 10 or newer.
- Python 3.9+.
- [Chainsaw](https://github.com/your-chainsaw-link) executable.
- Sigma rules and mappings (`rules/` folder and `mappings/sigma-event-logs-all.yml`) in the same directory as the Chainsaw executable.
- Python modules:
  ```bash
  pip install pywin32
  ```

---

## Installation

1. Clone or download this repository:
    ```bash
    git clone https://github.com/yourusername/your-repo.git
    cd your-repo
    ```

2. Ensure the Chainsaw executable is present. On first run, you can browse to select it.

---

## Usage

Run the script:

```bash
python chainsaw-scanner-menu.py
```

1. Choose `[1] Scan a folder or mounted image containing EVTX files`.
2. Select the folder containing EVTX files.
3. Select a folder to save reports.
4. Enter a case name for easy identification.
5. Chainsaw will scan the files using Sigma rules and save reports in CSV format.
6. Reports open automatically in Windows Explorer after scanning.

---

## Notes

- The tool will automatically create a `chainsaw-config.txt` file storing the path to your Chainsaw executable for future runs.
- Ensure the Sigma `rules/` folder and `mappings/sigma-event-logs-all.yml` are in the same directory as the Chainsaw executable.
- Running the script may request administrator privileges for certain operations.

---

## Screenshots

<img width="976" height="506" alt="image" src="https://github.com/user-attachments/assets/f04d3310-c9ac-48c7-8eb1-a996b80ee4c3" />

<img width="661" height="321" alt="image" src="https://github.com/user-attachments/assets/81b5fc54-e76e-43b4-99c8-415cfea71f2b" />



---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
