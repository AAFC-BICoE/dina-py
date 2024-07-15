## Object Upload Demo (Windows)

* Install Python 3.12.4 by downloading the installer from the following link and double click to open https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe, opt to 'Add Python to PATH' when asked during installation.
* Download the dina-py zip from the following link https://github.com/AAFC-BICoE/dina-py/archive/refs/heads/dev.zip and place it in **C:\Users\\<your_account>**
* Extract the .zip file 
* Open a Command Prompt terminal by pressing the 'Windows' key and typing in 'Command Prompt'
* In the Command Prompt terminal, change directory into the dina-py folder
```py
C:\Users\<your_account> cd dina-py
```
* Create a Python virtual environment (venv) using the following command, replacing variables such as <venv_name> with a name of your choice:
```py
C:\Users\<your_account>\dina-py> python -m venv <venv_name>
```
This should create a <venv_name> folder
* Activate the venv by executing the .bat file. You can tell the venv is active if there is a **(<venv_name>)** in front of the normal directory path. This is necessary everytime before using dina-py:
```py
C:\Users\<your_account>\dina-py> <venv_name>\Scripts\activate.bat
(.venv) C:\Users\<your_account>\dina-py>
```
* Install the dina-py project
```py
(.venv) C:\Users\<your_account>\dina-py> pip install .
```
* Make a copy of **keycloak-config-sample.yml** and rename to **keycloak-config.yml** in the root of dina-py directory, open **keycloak-config.yml** using Notepad
* In **keycloak-config.yml**, change **url, keycloak_username, keycloak_password** as needed
* From the dina-py directory's root, create a folder <object_upload_dir> containing the files to be uploaded
* From the dina-py directory's root, run the following command to upload all contents in <object_upload_dir>:
```py
(.venv) C:\Users\<your_account>\dina-py> python .\dinapy\client\dina_api_client.py -upload_dir '<object_upload_dir>' -group <user_group>
```
* Or run the following command to upload a specific file:
```py
(.venv) C:\Users\<your_account>\dina-py> python .\dinapy\client\dina_api_client.py -upload_file '<object_upload_dir>/<file_name>' -group <user_group>
```