## Windows 10 and 11

> **Note**
>
>It is mandatory to have python [3.10](https://www.python.org/downloads/release/python-31010/) (The official one, not the one from Microsoft Store) and [git](https://git-scm.com/download/win) installed.

### Prerequisites

Before you continue make sure you have these aditional applications installed:

Lately some bindings use Nvidia GPU (CUDA) for computing and is 3x faster than CPU. In order to run these bindings on CUDA device, you will need to install cuda toolkit.

- [Nvidia CUDA toolkit 11.7 or higher](https://developer.nvidia.com/cuda-downloads)

For CUDA and other packages to be compiled you will also need C++ build tools. The easiest way is to download Visual studio community. Make sure you choose C++ build tools at the installation screen.

- [Visual Studio Community](https://visualstudio.microsoft.com/vs/community/)

After these two are installed make sure to reboot your system before continuing.

### Manual Simple install:

1. Download this repository .zip:

![image](https://user-images.githubusercontent.com/80409979/232210909-0ce3dc80-ed34-4b32-b828-e124e3df3ff1.png)

2. Extract contents into a folder.
3. Install/run application by double clicking on `webui.bat` file from Windows Explorer as normal user.

### Manual Advanced mode:

1. Install [git](https://git-scm.com/download/win).
2. Open Terminal/PowerShell and navigate to a folder you want to clone this repository.

```bash
git clone https://github.com/ParisNeo/lollms-webui.git
```

4. Install/run application by double clicking on `webui.bat` file from Windows explorer as normal user and follow the on screen instructions.

## Linux

### Prerequisites

> **Note**
>
>This was tested on Ubuntu 22.04 or higher.

Before you continue make sure you have these aditional applications installed:

Lately some bindings use Nvidia GPU (CUDA) for computing and is 3x faster than CPU. In order to run these bindings on CUDA device, you will need to install cuda toolkit.

```bash
sudo apt install nvidia-cuda-toolkit
```

For CUDA and other packages to be compiled you will also need C++ build tools. The easiest way is to download Visual studio community. Make sure you choose C++ build tools at the installation screen.

```bash
sudo apt install build-essential
```

After these two are installed make sure to reboot your system before continuing.

### Automatic install

1. Make sure you have installed `curl`. It is needed for the one-liner to work.

`Debian-based:`
```
sudo apt install curl 
```
`Red Hat-based:`
```
sudo dnf install curl 
```
`Arch-based:`
```
sudo pacman -S curl 
```
2. Open terminal/console copy and paste this command and press enter: 
```
mkdir -p ~/lollms-webui && curl -L https://raw.githubusercontent.com/nomic-ai/lollms-webui/main/webui.sh -o ~/lollms-webui/webui.sh && chmod +x ~/lollms-webui/webui.sh && cd ~/lollms-webui && ./webui.sh
```
> **Note**
>
> This command creates new directory `/lollms-webui/` in your /home/ direcory, downloads a file [webui.sh](https://raw.githubusercontent.com/nomic-ai/lollms-webui/main/webui.sh), makes file executable and executes webui.sh that downloads and installs everything that is needed.

3. Follow instructions on screen until it launches webui.
4. To relaunch application: 
```
bash webui.sh
```

### Manual Simple install:

1. Download this repository .zip:

![image](https://user-images.githubusercontent.com/80409979/232210909-0ce3dc80-ed34-4b32-b828-e124e3df3ff1.png)

2. Extract contents into a folder.
3. Install/run application from terminal/console: 
```
bash webui.sh
```
### Manual Advanced mode:

1. Open terminal/console and install dependencies:

`Debian-based:`
```
sudo apt install curl git python3 python3-venv
```
`Red Hat-based:`
```
sudo dnf install curl git python3
```
`Arch-based:`
```
sudo pacman -S curl git python3
```

2. Clone repository:

```bash
git clone https://github.com/ParisNeo/lollms-webui.git
```
```bash
cd lollms-webui
```

3. Install/run application:

```bash
bash ./webui.sh
```

## MacOS

1. Open terminal/console and install `brew`:

```
$ /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install dependencies:

```
brew install git python3
```

3. Clone repository:

```bash
git clone https://github.com/ParisNeo/lollms-webui.git
```
```bash
cd lollms-webui
```

4. Install/run application:

```bash
bash ./webui.sh
```

On Linux/MacOS, if you have issues, refer to the details presented [here](docs/Linux_Osx_Install.md)
These scripts will create a Python virtual environment and install the required dependencies. It will also download the models and install them.
