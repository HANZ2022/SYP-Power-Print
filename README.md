# SYP-Power-Print
 It is a Senior Year Project for Dalhousie University students. The project aims to implement the initial positioning of a handheld printer on a flat surface using computer vision methods. It utilizes template matching to locate the target pattern within a specified plane for position tracking.

 ![Data_flow](https://github.com/user-attachments/assets/eb2fc89a-5641-4ef6-ba57-613e77cf2537)
# Raspberry Pi Camera Detection System

A detection system utilizing **Raspberry Pi Camera 3** and **Raspberry Pi 5** for capturing the workspace images and processing.

## Table of Contents
- [Hardware and Software Requirements](#Hardware-and-Software-Requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Menu Options](#menu-options)
  - [Parameter Adjustment](#parameter-adjustment)
- [File Structure](#file-structure)
- [Notes](#notes)
- [Contact](#contact)
- [Attachments](#Attachments)
  - [Re-Flashing Operation System](#1.-Steps-for-Re\-flashing-the-Operating-System)


---
## Hardware and Software Requirements
### Hardware
#### Required Hardware
- Raspberry Pi 5 (8G RAM) with a TransFlash card
- Raspberry Pi Camera 3 Wide
- CSI/DSI Flexible Cable (22Pin to 15Pin)

CSI/DSI Flexible Cable is used to connect the camera to the Raspberry Pi. The data interface of Raspberry Pi 5 is different from that of previous versions. Thus we need CSI/DSI (22Pin to 15Pin) cable.

#### Optional Hardware
- Micro/HDMI Adapter:
- USB Reader
- Raspberry Pi Case with a Cooling Fan

1. Micro/HDMI Adapter: 
This cable can connect the Raspberry Pi to the monitor. This way, you can operate the Raspberry Pi directly using a keyboard, mouse, and monitor.

2. USB Reader: 
When you need to re-flash the operating system, you will need this card reader to connect your computer to the Raspberry Pi's TF memory card.

3. Raspberry Pi Case with a Cooling Fan：
    Protect the hardware and assist in heat dissipation.


### Software
Software in Raspberry Pi
- Raspberry Pi OS (Raspbian GNU/Linux 12 (bookworm)), download this: (Raspberry Pi OS with desktop and recommended software)
  Download from [here](https://www.raspberrypi.com/software/operating-systems)
- Python 3.11.2

If you need to access the Raspberry Pi remotely, download a software that enables SSH remote access on the desktop.
- MobaXterm (Recommended) Download from [here](https://mobaxterm.mobatek.net/download.html)


### Dependencies
- `opencv-python`
- `numpy`
- `picamera2`

---

## Installation

### Step 1: Install Dependencies
Run the following commands on your Raspberry Pi:
```bash
sudo apt update
sudo apt install python3-opencv python3-pip -y
pip3 install numpy picamera2
```

### Step 2: Clone the Repository
Clone this repository to your Raspberry Pi:
```bash
git clone <repository_url>
cd <repository_directory>
```

### Step 3: Run the Application
Launch the application with:
```bash
python3 detect.py
```

---

## Usage

### Menu Options
After starting the program, a menu will appear with the following options:
1. **Start Detection**: Begin real-time template matching.
2. **Adjust Parameters**: Configure region boundaries and template images.
3. **Modify Camera Mode**: Switch between different camera resolutions.
4. **Change Parameter Folder**: Manage parameter files and configurations.
5. **Exit Program**: Close the application.

### Parameter Adjustment
Select **Adjust Parameters** from the menu to perform the following:
- **Set Region Boundaries**: Manually select the four corners of the region of interest.
- **Set Real Size**: Input the actual dimensions (in millimeters) of the region.
- **Set Template Image**: Manually select and save the template image for detection.

---

## File Structure
- **`detect.py`**: Main script for user interaction and mode selection.
- **`parameters_helper.py`**: Class for managing adjustable parameters (ROI, templates, etc.).
- **`detect_helper.py`**: Classes for camera control and detection processing.

---

## Notes
- Ensure the Camera 3 is correctly connected and enabled before running the application.
- All parameter files are stored in the `parameters_support` folder, with separate subfolders for each configuration.

---

## Attachments
### 1. Steps for Re-flashing the Operating System
1. The App used to re-flash the operation:

![step1](https://github.com/user-attachments/assets/48ecf000-4cd5-4b19-964f-5e8eaa5ffb22)

2. Select the Downloaded Operating System Image File:

![step2](https://github.com/user-attachments/assets/6bdbb1f5-747a-4323-aa8a-22e626ba64a9)
![step3](https://github.com/user-attachments/assets/e747f7a9-8ef2-4c13-9960-687b657a5b0f)

3. Select Your TF Memory Card:

![step4](https://github.com/user-attachments/assets/1129f9d1-0ee1-46d8-ad27-6859490e4d26)

4. Starting Flashing:

![step5](https://github.com/user-attachments/assets/0bb9cd30-0cdf-4e1a-b999-818250587e94)

---

## Contact
For support or feedback, please contact the repository maintainer.


