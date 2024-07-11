## Object Upload Demo (Windows)

* Install Python (3.10 or above, tested with 3.12), opt to 'Add Python to PATH' when asked during installation.
* Open a command prompt terminal and clone the dina-py repo:
```py
C:\> git clone -b dev https://github.com/AAFC-BICoE/dina-py.git
```
* Change directory into the dina-py folder
```py
C:\dina-py> cd dina-py
```
* Create a Python virtual environment (venv):
```py
C:\dina-py> python -m venv <venv_name>
```
This should create a <venv_name> folder
* Activate venv by executing the .bat. You can tell the venv is active if there is a (<venv_name>) in front of the normal directory path:
```py
C:\dina-py> <venv_name>\Scripts\activate.bat
(.venv) C:\dina-py>
```
* Install the dina-py project
```py
(.venv) C:\dina-py> pip install .
```
* Make a copy of **keycloak-config-sample.yml** and rename to **keycloak-config.yml** in the root of dina-py directory
* In **keycloak-config.yml**, change **url, keycloak_username, keycloak_password** as needed
* From the dina-py directory's root, create a folder <object_upload_dir> containing the files to be uploaded
* From the dina-py directory's root, run the following command to upload all contents in <object_upload_dir>:
```py
(.venv) C:\dina-py> python .\dinapy\client\dina_api_client.py -upload_dir '<object_upload_dir>' -group <user_group>
```
* Or run the following command to upload a specific file:
```py
(.venv) C:\dina-py> python .\dinapy\client\dina_api_client.py -upload_file '<object_upload_dir>/<file_name>' -group <user_group>
```