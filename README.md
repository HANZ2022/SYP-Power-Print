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
- [Operation process](#Operation-process)
- [Notes](#notes)
- [Contact](#contact)
- [Attachments](#Attachments)
  - [Re-Flashing Operation System](#Steps-for-Flashing-the-Operating-System)
  - [Remote Access](#Steps-for-Remote-Access)


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
- Raspberry Pi OS (Raspbian GNU/Linux 12 (bookworm), download (Raspberry Pi OS with desktop and recommended software) from [here](https://www.raspberrypi.com/software/operating-systems). Please refer to [here](#Steps-for-Flashing-the-Operating-System) for the flashing steps.
- Python 3.11.2

If you need to access the Raspberry Pi remotely, download a software that enables SSH remote access on the desktop.
- MobaXterm (Recommended) Download from [here](https://mobaxterm.mobatek.net/download.html)
- An instruction on how to use the software to access the RaspberryPi remotely can be found in the appendix, click [here](#Steps-for-Remote-Access)


### Dependencies
- `opencv-python`
- `numpy`
- `picamera2`

---

## Installation

### Step 1: Install Dependencies
Download the lib
```bash
pip install --upgrade pip
sudo apt install python3-opencv python3-pip -y
```

### Step 2: Clone the Repository
Run the following commands on your Raspberry Pi:
```bash
cd Desktop
```
Clone this repository to your Raspberry Pi:
```bash
git clone <repository_url>
cd <repository_directory>
```
After downloading the folder into Desktop, then enter the folder
```bash
cd SYP-Power-Print
```

### Step 3: Run the Application
Run the python code:
```bash
python detect.py
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

## Operation process
1. python detect.py
2. Select the resolution
3. Select an existing parameter folder or create a new one
4. Start to modify the parameters.
5. Select the corners of the region of interest firstly.
6. Cropping for the target template secondly.
7. Modifying the real dimensions of the region of interest.
8. Start detecting.
   A demonstration video can be found [​here](https://www.youtube.com/watch?v=Vo7g2HlLYls)
---

## Notes
- When operating, please read the prompt words shown in the terminal carefully. It will tell you what you need to do.
- Ensure the Camera 3 is correctly connected and enabled before running the application.
- All parameter files are stored in the `parameters_support` folder, with separate subfolders for each configuration.
- When cropping the target pattern, when a blue area appears in the displayed window that was not there before, it means that the program is ready to crop.
- When you are cropping an image, make sure the system focuses on the image window. For example, when cropping, the terminal will prompt you to use the keyboard to cancel, continue, exit, etc. Make sure that the image window is the window selected by your mouse before using the keyboard.
- Every time the relative position of the camera and the region of interest changes, all parameters need to be reset.
---

## Attachments
### Steps for Flashing the Operating System
1. The App used to re-flash the operation, download from [here](https://www.raspberrypi.com/software):

![Step1](https://github.com/user-attachments/assets/b6f41eee-8a4d-445d-a70f-5fb8267ee78a)


2. Select the Downloaded Operating System Image File or download online from the options in list:

![Step2](https://github.com/user-attachments/assets/3019d8a8-8e26-4ca6-a6bc-71394e1c587a)

3. Apply Customized Setting:

![Step3](https://github.com/user-attachments/assets/cca3e70a-eb0c-4ae5-ad01-a7a5c998033e)

- Pre-setting the the WIFI. The author used his own mobile phone's hotspot as the network here. Some public networks may not be able to be connected due to certificate issues (for example, the school network cannot be directly connected).

![Step4](https://github.com/user-attachments/assets/adc84258-351e-465b-9678-e085b077fbc1)

- If you want to use password:

![Step 5](https://github.com/user-attachments/assets/d21c6059-3af3-4509-abc6-443f53a3bfb3)

- If you trust the device you are using: 

![Step5](https://github.com/user-attachments/assets/abd457b9-5707-488e-8dcf-b41172b070a1)


### Steps for Remote Access
The software used here is MobaXterm. Download from [here](https://mobaxterm.mobatek.net/download.html).
1. Create a new session and select SSH:

![Step 1](https://github.com/user-attachments/assets/8ef238f6-bb44-4a60-ab4f-239dbc5cb16f)

![Step 2](https://github.com/user-attachments/assets/7e2a485c-e1cd-4f25-9771-6463eddbb4af)

2. Type the host name or host IP of the Raspberry Pi, the port number is 22.

![Step 3](https://github.com/user-attachments/assets/0bf53255-5f29-490d-9089-61b91f4c8413)


## Contact
For support or feedback, please contact the repository maintainer.




