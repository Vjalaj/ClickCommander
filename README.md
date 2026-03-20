# ⚡ ClickCommander

<p align="center">
  <img src="logo.svg" alt="ClickCommander Logo" width="200"/>
</p>

<p align="center">
  <strong>The ultimate automation powerhouse for Windows</strong><br>
  Record, replay, and automate your mouse movements, clicks, and keyboard inputs with surgical precision.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version"/>
  <img src="https://img.shields.io/badge/platform-windows-lightgrey.svg" alt="Platform"/>
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"/>
  <img src="https://img.shields.io/badge/status-active-success.svg" alt="Status"/>
</p>

---

## 🎯 What is ClickCommander?

ClickCommander is a **powerful Python-based automation tool** that captures and replays your every move with pixel-perfect accuracy. Whether you're testing software, automating repetitive tasks, or creating complex workflows, ClickCommander delivers unmatched precision and control.

**Why ClickCommander?**
- 🎯 **Zero Learning Curve** — Just record and play
- ⚡ **Lightning Fast** — Replays at your exact speed
- 🔒 **100% Local** — Your data never leaves your machine
- 🎮 **Full Control** — Pause, resume, and loop with ease

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🖱️ Mouse Automation
- **Pixel-Perfect Tracking** — Records every movement
- **All Click Types** — Left, right, middle clicks
- **Drag & Drop** — Seamless drag operations
- **Scroll Support** — Exact scroll distance & speed

</td>
<td width="50%">

### ⌨️ Keyboard Automation
- **Full Typing Capture** — Every keystroke recorded
- **Special Keys** — Enter, Tab, Shift, Ctrl, etc.
- **Exact Timing** — Preserves your typing speed
- **Unicode Support** — Works with all characters

</td>
</tr>
<tr>
<td width="50%">

### 🎮 Playback Control
- **Loop Automation** — Run 1 to ∞ times
- **Custom Delays** — Set gaps between runs
- **Pause/Resume** — Full playback control
- **Global Hotkeys** — Control from anywhere

</td>
<td width="50%">

### ⚡ Performance
- **Zero Lag** — Instant response time
- **Minimal Overhead** — Lightweight recording
- **Exact Replay** — Timing preserved perfectly
- **No Failsafe** — Uninterrupted automation

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8 or higher** — [Download Python](https://www.python.org/downloads/)
- **Windows OS** — Windows 10/11 recommended
- **Administrator privileges** — Required for global hotkeys

### Installation

#### Step 1: Clone the Repository

```bash
git clone https://github.com/Vjalaj/ClickCommander.git
cd ClickCommander
```

#### Step 2: Create Virtual Environment (Recommended)

Using a virtual environment keeps your project dependencies isolated and prevents conflicts.

**Create the virtual environment:**
```bash
python -m venv venv
```

**Activate the virtual environment:**
```bash
# On Windows (Command Prompt)
venv\Scripts\activate

# On Windows (PowerShell)
venv\Scripts\Activate.ps1

# On Windows (Git Bash)
source venv/Scripts/activate
```

💡 **Tip:** You'll see `(venv)` in your terminal when the virtual environment is active.

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**
- `pyautogui` — Mouse and keyboard automation
- `pynput` — Input event monitoring
- `keyboard` — Global hotkey detection

---

## 🎮 How to Use

### Starting ClickCommander

1. **Activate your virtual environment** (if not already active):
   ```bash
   venv\Scripts\activate
   ```

2. **Run the script**:
   ```bash
   python auto_clicker.py
   ```

3. **Configure your automation**:
   ```
   How many times should the auto clicker run? 10
   Gap between consecutive runs (seconds)? 2
   ```

### Hotkey Controls

<table>
<thead>
<tr>
<th>Hotkey</th>
<th>Action</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>Ctrl + Alt + R</code></td>
<td><strong>Stop Recording</strong></td>
<td>Saves your recorded actions and prepares for playback</td>
</tr>
<tr>
<td><code>Ctrl + Alt + P</code></td>
<td><strong>Play</strong></td>
<td>Starts playback of recorded actions</td>
</tr>
<tr>
<td><code>Ctrl + Alt + P</code></td>
<td><strong>Pause</strong></td>
<td>Pauses playback (press again to resume)</td>
</tr>
</tbody>
</table>

### Workflow Example

```
┌─────────────────────────────────────────────────────────────┐
│  1. START SCRIPT → Recording begins automatically          │
│  2. PERFORM ACTIONS → Move, click, type, drag, scroll      │
│  3. PRESS Ctrl+Alt+R → Stop and save recording             │
│  4. PRESS Ctrl+Alt+P → Start playback                      │
│  5. PRESS Ctrl+Alt+P → Pause (optional)                    │
│  6. PRESS Ctrl+Alt+P → Resume (optional)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ What Gets Recorded?

ClickCommander captures **everything** with perfect timing:

| Action | Captured | Details |
|--------|----------|----------|
| 🖱️ **Mouse Movement** | ✅ | Every pixel of movement |
| 👆 **Clicks** | ✅ | Left, right, middle buttons |
| 🎨 **Drag & Drop** | ✅ | Complete drag operations |
| 🔄 **Scroll** | ✅ | Exact scroll distance & speed |
| ⌨️ **Typing** | ✅ | All characters and symbols |
| 🔑 **Special Keys** | ✅ | Enter, Tab, Shift, Ctrl, Alt, etc. |
| ⏱️ **Timing** | ✅ | Precise delays between all events |

---

## 🎯 Use Cases

<table>
<tr>
<td width="33%" align="center">

### 🧪 Software Testing
Automate repetitive test scenarios and regression testing

</td>
<td width="33%" align="center">

### 📊 Data Entry
Speed up form filling and data input tasks

</td>
<td width="33%" align="center">

### 🎮 Gaming
Create macros for repetitive in-game actions

</td>
</tr>
<tr>
<td width="33%" align="center">

### 🖼️ Design Work
Automate repetitive design and editing tasks

</td>
<td width="33%" align="center">

### 📝 Documentation
Record workflows for tutorials and guides

</td>
<td width="33%" align="center">

### 🔄 Batch Processing
Process multiple files with identical steps

</td>
</tr>
</table>

---

## ⚙️ Configuration

### Adjusting Playback Settings

When you start the script, you can configure:

- **Number of runs** — How many times to repeat (1 to unlimited)
- **Gap between runs** — Delay in seconds between each repetition

**Example configurations:**

```bash
# Run once with no delay
Runs: 1
Gap: 0

# Run 100 times with 5-second gaps
Runs: 100
Gap: 5

# Run continuously (set a high number)
Runs: 999999
Gap: 1
```

---

## ⚠️ Important Notes

### Before You Start

- ✅ **Run as Administrator** — Required for global hotkey detection
- ✅ **Same Screen Resolution** — Recordings are resolution-specific
- ✅ **Stable Environment** — Ensure windows/apps are in the same position
- ✅ **Test First** — Always test with 1 run before setting high repeat counts

### Safety Features

- 🔴 **Failsafe Disabled** — Moving mouse to corner won't stop the script
- 🎮 **Use Hotkeys** — Always use `Ctrl+Alt+P` to pause/stop playback
- ⚡ **Exact Speed** — Playback matches your recording speed perfectly
- 💾 **No File Saving** — Recordings are stored in memory (restart to clear)

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Hotkeys not working | Run as Administrator |
| Mouse moves too slow | Already fixed - runs at exact speed |
| Scroll not working | Ensure you're scrolling during recording |
| Keyboard not typing | Check if target app accepts input |
| Virtual environment issues | Deactivate and reactivate: `deactivate` then `venv\Scripts\activate` |

---

## 📋 Requirements

### System Requirements

- **OS:** Windows 10/11 (64-bit recommended)
- **Python:** 3.8 or higher
- **RAM:** 256 MB minimum
- **Disk Space:** 50 MB for installation

### Python Dependencies

```txt
pyautogui>=0.9.53
pynput>=1.7.6
keyboard>=0.13.5
```

All dependencies are automatically installed via `requirements.txt`.

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute

- 🐛 **Report Bugs** — Found an issue? [Open an issue](https://github.com/Vjalaj/ClickCommander/issues)
- 💡 **Suggest Features** — Have an idea? We'd love to hear it!
- 🔧 **Submit Pull Requests** — Code contributions are always welcome
- 📖 **Improve Documentation** — Help make our docs even better
- ⭐ **Star the Repo** — Show your support!

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/Vjalaj/ClickCommander.git
cd ClickCommander

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Make your changes and test
python auto_clicker.py

# Submit a pull request
```

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

**TL;DR:** You can use, modify, and distribute this software freely. Just keep the original license notice.

---

## 🌟 Show Your Support

If ClickCommander saves you time and makes your life easier:

- ⭐ **Star this repository** on GitHub
- 🐦 **Share it** with your friends and colleagues
- 💬 **Spread the word** on social media
- ☕ **Buy us a coffee** (coming soon!)

---

## 📞 Support & Contact

- 🐛 **Issues:** [GitHub Issues](https://github.com/Vjalaj/ClickCommander/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/Vjalaj/ClickCommander/discussions)
- 📖 **Documentation:** [Wiki](https://github.com/Vjalaj/ClickCommander/wiki)

---

## 🎉 Acknowledgments

Built with ❤️ using:
- [PyAutoGUI](https://pyautogui.readthedocs.io/) — Cross-platform GUI automation
- [pynput](https://pynput.readthedocs.io/) — Monitor and control input devices
- [keyboard](https://github.com/boppreh/keyboard) — Hook and simulate keyboard events

---

<p align="center">
  <strong>Made with ⚡ by developers, for developers</strong><br>
  <sub>Automate everything. Focus on what matters.</sub>
</p>

<p align="center">
  <a href="#-clickcommander">Back to Top ↑</a>
</p>
