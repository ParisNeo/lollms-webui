# Installing lollms-webui on Linux or macOS:

\- Make sure you have all the dependencies for requirements
`python3.11 -m pip install cmake`
`python3.11 -m pip install nproc` if you have issues with scikit-learn add the foollowing env var
`SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True` 
`python3.11 -m pip install wget`

\- Install requirements  
python3.11 -m pip install -r requirements.txt 

![](https://user-images.githubusercontent.com/9384127/230159652-120e60f3-b737-434a-ac01-15819a0e7698.png)

\- Review the install script 🙏🏻

```
nano -lASimYsh install.sh
```

![](https://user-images.githubusercontent.com/9384127/229646387-9fea98c6-fb13-496b-b8eb-9db6fe241556.png)

\- Make it runnable

```
chmod +x install.sh
```

\- Run the install script

```
./install.sh
```

![](https://user-images.githubusercontent.com/9384127/229650379-e70a54b3-a8c0-44c6-a44f-26b96dfbcf4e.png)

\- Install nomic 

```
pip install nomic
```

or force pip to install with Python 3.11

```
python3.11 -m pip install nomic
```

![](https://user-images.githubusercontent.com/9384127/229660511-ea6ef97e-712a-4e59-81d4-b4162e796728.png)

![](https://user-images.githubusercontent.com/9384127/229660570-a960cfc3-4634-4354-868f-259ba9ffe888.png)

\- Install/updt venv 

```
sudo apt install python3.11-venv
```

![](https://user-images.githubusercontent.com/9384127/229801745-3c84e89e-c62c-460d-9e79-dafe5aa518d5.png)

\- ToDo

