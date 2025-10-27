
# 🏰 WatchTower  
> “Because your camera should do more than just stare blankly.”

Welcome to **WatchTower** — a low-key, high-power desktop app for **real-time camera monitoring**, **motion detection**, and **automatic video logging**.  
Built with pixels, caffeine, and a *suspiciously tiny number of `print()`s*, WatchTower is your digital sentry — watching so you don’t have to.

Whether you’re guarding your cat’s criminal activities, securing your workspace, or just flexing your setup — **WatchTower** has your back.

---

## 🛠️ Features

- 📷 **Real-time motion detection** using background subtraction  
- 🧠 **Human/face detection** powered by OpenCV  
- 🎥 **Automatic recording** with pre/post buffer  
- 💾 **Auto clip saving** & export options  
- ⚙️ **Customizable settings wizard** for camera, storage, and preferences  
- 🧙 **Minimal GUI** (PyQt5 or tkinter) with live preview  
- 🧩 **Keyboard shortcuts** for quick control  
- 🔇 **Zero background noise** — unless *you* add the sound effects  
- 🕶️ **Background mode** for stealth operation  

---

## 🚀 Quick Start

1. Download the latest `.exe` installer from the [Releases page](https://github.com/rijultheone/WatchTower/releases)  
2. Run → Install → Launch  
3. Let the surveillance sorcery begin.  

---

## 🧪 Dev Setup (for the curious or chaotic)

```bash
# Clone the repo
git clone https://github.com/<your-username>/watchtower-app.git
cd watchtower-app

# Install dependencies
pip install -r requirements.txt

# Run the app
python watchtower/main.py
```

```
┌───────────── WATCHTOWER PROJECT ─────────────┐
│ NAME:       WatchTower                      │
│ VERSION:    v1.0.0-Beta                     │
│ GENRE:      Surveillance Wizardry (w/ GUI)  │
│ CREATED:    25•07•2025                      │
└─────────────────────────────────────────────┘
```

---

## 🧭 Configuration

On first run, the setup wizard will help you configure:
- 📸 Camera selection  
- 💾 Storage location  
- ⚙️ Recording & detection settings  

All preferences are stored in `~/.watchtower_config.json`.  
You can edit it manually or use the built-in settings panel.

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|---------|
| **Space** | Start / Stop recording |
| **Esc** | Close current window |
| **Q** | Quit application |
| **D** | Toggle debug overlay |
| **Ctrl + F** | Toggle fullscreen |
| **Ctrl + B** | Run in background |
| **S** | Open settings |

---

## 🤝 Contributing

1. **Fork** the repository  
2. **Create** your feature branch → `git checkout -b feature/amazing-feature`  
3. **Commit** your changes → `git commit -m 'Add some amazing feature'`  
4. **Push** to your branch → `git push origin feature/amazing-feature`  
5. **Open** a Pull Request  

---

## 📜 License

This project is licensed under the **MIT License** — see the `LICENSE` file for details.  

---

## 💡 Acknowledgments

- 🧠 [OpenCV](https://opencv.org/) — for powering motion and face detection  
- 🐍 The Python community — for their excellent tools and libraries  
- ☕ Caffeine — for late-night bug fixing and code wizardry

