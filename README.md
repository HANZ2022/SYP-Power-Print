# SYP-Power-Print
 It is a Senior Year Project for Dalhousie University students. The project aims to implement the initial positioning of a handheld printer on a flat surface using computer vision methods. It utilizes template matching to locate the target pattern within a specified plane for position tracking.

--- ![Data_flow](https://github.com/user-attachments/assets/eb2fc89a-5641-4ef6-ba57-613e77cf2537)
# Raspberry Pi Camera Detection System

A detection system utilizing **Raspberry Pi Camera 3** and **Raspberry Pi 5** for capturing the workspace images and processing.

## Table of Contents
- [Modules Used for the project](#Modules-Used-for-the-Project)
- [Hardware and Software Requirements](#hardware-and-software-requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Menu Options](#menu-options)
  - [Parameter Adjustment](#parameter-adjustment)
- [File Structure](#file-structure)
- [Notes](#notes)
- [Contact](#contact)


---
## Modules Used for the Project

## Hardware and Software Requirements

### Hardware
- Raspberry Pi 5
- Raspberry Pi Camera 3

### Software
- Raspberry Pi OS (Official OS)

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

## Contact
For support or feedback, please contact the repository maintainer.


