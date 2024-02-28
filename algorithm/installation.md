## Getting Started

### Using Virtual Environments
To get started, install the virtualenv tool with pip:
  ```sh
  pip install virtualenv
  ```
The __installation.txt__ file will contain all the details related to the external packages that we have installed along with their versions. You can create the virtual machine again easily by downloading all the same libraries, having the same versions by a simple command. 
  ```sh
  pip install package_name == version
  ```
#### For MacOS
Install all the packages at once by using the requirement.txt file:
  ```sh
  pip install -r requirements.txt
  ```
To activate your virtual environment, run the code below:
  ```sh
  source .venv/bin/activate
  ```
Once the virtual environment is activated, the name of your virtual environment will appear on the terminal's left side like 
  ```sh
  (virtualenv_name)$ 'your command'
  ```
To deactivate your virtual environment, simply run the following code in the terminal:
  ```sh
  deactivate
  ```

#### For Windows
Install all the packages at once by using the requirement.txt file:
  ```sh
  pip install -r .\requirements.txt
  ```
To activate your virtual environment, run the code below:
  ```sh
  .\.venv\bin\activate
  ```
Once the virtual environment is activated, the name of your virtual environment will appear on the terminal's left side like 
```sh
(virtualenv_name)$ 'your command'
```
To deactivate your virtual environment, simply run the following code in the terminal:
  ```sh
  deactivate
  ```




