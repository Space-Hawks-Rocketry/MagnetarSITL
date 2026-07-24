# HawkSITL

## Table of Contents
1. [What is SITL?](#what-is-sitl)
2. [Intro to HawkSITL Template](#intro-to-hawksitl-template)
3. [Setup and Installation](#setup-and-installation)
4. [Usage (With Examples)](#usage-with-examples)

## What is SITL?
SITL (or software-in-the-loop) is a type of simulation capable of testing flight software before ever launching. 
Instead of on an embedded device, flight software is run on your computer, real hardware sensor data is replaced with simulation-generated
sensor readings, and the flight software sends control commands to the environment instead of to external hardware.

### SITL Enables:
* Quick software development cycle (no uploading code or sharing hardware).
* Sim-truth to compare against navigation computer estimates.
* More robust testing before flight.
  * Randomized environment conditions (such as wind).
  * Simulated sensor faults.
  * Completely free, break anything.
* Often closed-loop:
  * The environment affects the rocket.
  * Rocket control decisions affect the environment.

### SITL Limitations:
* Accuracy depends on environment models:
  * Atmospheric models
  * 6DOF model
  * Sensor models
  * Rocket model
* Cannot test hardware-interfacing firmware:
  * Sensor communication firmware.
  * Data logging firmware.

## Intro to HawkSITL Template
HawkSITL is the Space Hawks SITL framework enabling rapid flight software and GN&C prototyping. This repository serves as a template for
repositories attempting to use SITL testing for various projects.

### Goals of HawkSITL
In addition to typical SITL goals, we intend to:
* Make SITL projects portable between development environments, regardless of OS.
* Keep our framework lightweight and easy to use.
* Include basic models for general rocketry use.
* Enable easy transferability between SITL flight software and actual flight software.

### Architecture
The HawkSITL framework is split into two main parts:
* Environment (written entirely in **Python**)
* Flight Computer (written entirely in **C++**)

**SITL Communication Scheme**

<img width="449" height="244" alt="image" src="https://github.com/user-attachments/assets/ad151c4f-7d12-48e0-b907-15bfc0d82dff" />

*Made with Lucidchart.*

All communication exists user-defined JSON objects. HawkSITL requires no standards to be upheld, and only facilitates JSON communication so that
the framework user may supply sensor data and control commands in whatever format they choose.

#### User Directories
Most of the HawkSITL template is necessary framework code and should not be modified.

Here are the directories that you should work within (ideally):
* environment/simulation  -->  Define the environment models and simulation.
* flight-computer/src/simulation  --> Write flight software.
* flight-computer/include/simulation  --> Write flight software headers.

## Setup and Installation

Before installing HawkSITL, ensure the following software is installed.

### Required Software
Install these if they are not already installed:
* Git (also, configure GitHub SSH authentication)
* **For Windows:** WSL w/ Unbuntu-24.04 (follow this guide: https://ubuntu.com/wsl/docs/stable/howto/install-ubuntu-wsl2/)
* Docker Desktop
* Visual Studio Code

### Required VS Code Extensions
Install the following Visual Studio Code extensions:

* Dev Containers
* WSL (Windows only)

### Setting Up an SITL Project
Make a repository from this template:

<img width="249" height="188" alt="image" src="https://github.com/user-attachments/assets/14e991cb-b095-4422-bbc4-01151b514093" />

**Next:**
- Clone your repo into WSL (for Windows) or anywhere (for MacOS)
- In a terminal, navigate into the cloned repo's folder and run: ``` code . ```
- Press **Ctrl+Shift+P** in the opened VSCode instance, then run **Dev Containers: Reopen in Container**
- You should be good to go.

## Usage (With Examples)
For now, refer to any of the example branches (may not be up to date):
* <a href="https://github.com/Space-Hawks-Rocketry/HawkSITL_Template/tree/example/hovering-cube">Hovering Cube</a>


### Important Commands
Run these within your project directory:
* To build flight computer code: ```make build```
* To run simulation: ```make run```
* To build, then run simulation: ```make sitl```
* To clean project build: ```make clean```
