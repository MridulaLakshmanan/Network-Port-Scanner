# 🌐 Network Port Scanner

A modern, professional-grade network port scanning tool built with Python. Scan target hosts for open/closed ports with a sleek GUI, multithreaded performance, and real-time result visualization.

## ✨ Features

### Core Functionality
- **Fast Port Scanning**: Multithreaded scanning with configurable worker threads (1-500)
- **IP & Domain Support**: Scan by IP address or hostname (automatic DNS resolution)
- **Open/Closed Detection**: Identifies open and closed ports on target hosts
- **Service Detection**: Recognizes common services (HTTP, SSH, MySQL, etc.)
- **Custom Port Ranges**: Scan any port range from 1 to 65535

### User Interface
- **Modern Dark Theme**: Professional, eye-catching gradient design
- **Real-Time Updates**: Live port scanning results as they're discovered
- **Progress Indicator**: Visual progress bar during scans
- **Color-Coded Results**:
  - 🟢 Green: Open ports
  - ⚫ Gray: Closed ports
  - 🔵 Blue: Informational messages
  - 🔴 Red: Errors
  - 🟡 Orange: Warnings

### Advanced Features
- **Scan Timer**: Track scan duration in real-time
- **Stop Functionality**: Cancel ongoing scans at any time
- **Result Export**: Save results to `.txt` file with detailed report
- **Clear Results**: Reset scan results between scans
- **Input Validation**: Comprehensive validation for all inputs
- **Error Handling**: Graceful handling of network issues and invalid inputs

## 🎯 Requirements

- Python 3.8 or higher
- customtkinter 5.0.0+
- Standard library only (socket, threading, concurrent.futures)

## 📦 Installation

### 1. Clone or Download Project
```bash
cd network_port_scanner
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🚀 Usage

### Start the Application
```bash
python main.py
```

### Basic Scanning

1. **Enter Target**: Input IP address (e.g., `192.168.1.1`) or hostname (e.g., `google.com`)
2. **Set Port Range**: 
   - Start Port: `1` (default)
   - End Port: `1000` (default, adjust as needed)
3. **Configure Threads**: Leave at `50` for balanced performance
4. **Click "▶ Start Scan"**: Scanning begins immediately

### Example Scans

**Scan Common Web Ports**
- Target: `google.com`
- Start Port: `1`
- End Port: `1000`

**Scan SSH and Common Services**
- Target: `192.168.1.1`
- Start Port: `20`
- End Port: `30`

**Scan All Ports** (⚠️ Time-intensive)
- Target: `localhost`
- Start Port: `1`
- End Port: `65535`

## 📊 Understanding Results

### Output Format
```
[+] Port   80 OPEN   (HTTP)
[+] Port  443 OPEN   (HTTPS)
[-] Port   21 CLOSED (FTP)
[+] Port   22 OPEN   (SSH)
```

- `[+]` = Open port
- `[-]` = Closed port
- `(SERVICE)` = Service name running on port

## 🔒 Security & Ethics

⚠️ **IMPORTANT**: This tool is for **educational and authorized use only**.

- **Only scan systems you own or have explicit permission to scan**
- Unauthorized port scanning may be illegal in your jurisdiction
- Always obtain proper authorization before scanning
- This tool should not be used for malicious purposes

## 🏗️ Project Architecture

### File Structure
```
network_port_scanner/
├── main.py              # Application entry point
├── ui.py                # GUI implementation (customtkinter)
├── scanner.py           # Core port scanning engine
├── utils.py             # Helper functions & validators
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Module Overview

**scanner.py** - Port Scanning Logic
- `PortScanner`: Main scanning class
- Multithreaded scanning with ThreadPoolExecutor
- DNS resolution for hostnames
- Service name detection
- Input validation

**ui.py** - User Interface
- `PortScannerApp`: Main GUI window
- Modern dark theme with color-coded results
- Real-time scan updates
- Status bar with timer and progress
- File export functionality

**utils.py** - Utilities
- `ResultFormatter`: Format and export results
- `InputValidator`: Validate user inputs
- `TimeFormatter`: Format time durations
- `PortInfo`: Port and service information

## 💡 Usage Tips

### Performance Tips
- **Increase threads** (up to 100) for faster scans on large port ranges
- **Decrease threads** to 10-20 if experiencing connection issues
- Common ports (1-1024) typically scan quickly
- Large port ranges (e.g., 1-65535) may take considerable time

### Troubleshooting

**Scan Hangs**
- Click "⏹ Stop Scan" to cancel
- Try reducing the number of threads
- Check target host is reachable

**"Could not resolve" Error**
- Verify hostname spelling
- Check internet connection
- Try using IP address directly

**No Results Found**
- Target host may be offline or unreachable
- Firewall may be blocking connections
- Try broader port range (e.g., 1-100 first)

**Slow Scanning**
- Increase thread count (up to 100)
- Scan smaller port ranges
- Ensure network connection is stable

## 🔧 Customization

### Modify Default Port Range
Edit `ui.py`, in `_create_input_frame()`:
```python
self.end_port_input.insert(0, "1000")  # Change to your preference
```

### Adjust Socket Timeout
Edit `scanner.py`, in `__init__()`:
```python
def __init__(self, timeout: float = 1.5):  # Increase for slow networks
```

### Add More Service Names
Edit `scanner.py`, in `get_service_name()` or `utils.py` in `PortInfo.COMMON_PORTS`:
```python
5432: "PostgreSQL",
6379: "Redis",
# Add more mappings here
```

## 📋 Common Ports Reference

| Port | Service | Description |
|------|---------|-------------|
| 21 | FTP | File Transfer Protocol |
| 22 | SSH | Secure Shell |
| 53 | DNS | Domain Name System |
| 80 | HTTP | Web Server |
| 443 | HTTPS | Secure Web |
| 3306 | MySQL | Database |
| 5432 | PostgreSQL | Database |
| 3389 | RDP | Remote Desktop |
| 27017 | MongoDB | NoSQL Database |
| 6379 | Redis | In-Memory Cache |

## 📝 Technical Details

### Scanning Method
- Uses TCP connect() scans (reliable, detectable)
- Timeout: 1.5 seconds per port (adjustable)
- Thread pool: Up to 500 concurrent threads

### Supported Targets
- IPv4 addresses: `192.168.1.1`
- Hostnames: `example.com`
- Subdomains: `api.example.com`
- localhost: `localhost`, `127.0.0.1`

### Results Export
Exports include:
- Target host scanned
- Scan timestamp
- Total ports scanned
- List of open ports with services
- Sample of closed ports

## 🐛 Known Limitations

- IPv6 not supported (IPv4 only)
- Banner grabbing not implemented (service detection via port number only)
- No firewall rule detection
- No UDP scan support (TCP only)

## 🤝 Contributing

This is an educational project. Feel free to:
- Report bugs and issues
- Suggest new features
- Improve documentation
- Optimize performance

## ⚖️ License

This project is provided as-is for educational purposes. Use responsibly and legally.

## 📚 Learning Resources

- Socket Programming: https://docs.python.org/3/library/socket.html
- Threading: https://docs.python.org/3/library/threading.html
- CustomTkinter: https://github.com/TomSchimansky/CustomTkinter

## ✅ Checklist for First Run

- [ ] Python 3.8+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Run application: `python main.py`
- [ ] Test with localhost: Target `127.0.0.1`, ports `1-1000`
- [ ] Export a test scan to verify functionality
- [ ] Read security notice and understand ethical use

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready  

⚠️ **Remember**: Only scan systems with proper authorization!
