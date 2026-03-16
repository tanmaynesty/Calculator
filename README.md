# Calculator 🖩

A sleek, modern, and frameless calculator built entirely in Python using `tkinter`. This Calculator features a custom dark-mode user interface, rounded corners, a slide-out history panel, and a built-in memory system.

## 📸 Screenshots

![Calculator Main Interface](url-to-your-image/main-view.png)
*The main frameless UI with custom window controls.*

## ✨ Features

* **Custom Frameless UI:** Bypasses the default OS window decorations for a unified dark-mode look, complete with a custom drag-to-move title bar.
* **Advanced Operations:** Supports standard arithmetic, square root, squares, reciprocals, and percentages.
* **History Tracking:** A built-in, toggleable history panel (`HIST`) that logs calculations with timestamps.
* **Memory Functions:** Standard calculator memory operations (`MC`, `MR`, `MS`).
* **Quality of Life:** * **Click-to-Copy:** Right-click or middle-click the result display to copy the value to your clipboard (flashes green for visual feedback).
    * **Dynamic Resizing:** The font size scales down gracefully when expressions get too long.
    * **Keyboard Support:** Fully mapped to the number pad and standard keyboard.
* **Native Feel:** Uses Windows `ctypes` to apply native rounded corners to the main application window.

## 🚀 Getting Started

### Prerequisites
Calculator is built using standard Python libraries. You only need Python installed on your system.
* Python 3.x
* `tkinter` (Usually comes pre-installed with Python on Windows/macOS. On some Linux distributions, you may need to install it via your package manager, e.g., `sudo apt install python3-tk`).

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/OnyxCalc.git](https://github.com/yourusername/OnyxCalc.git)
