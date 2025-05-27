import os
import subprocess
import sys

venv_dir = os.path.join(os.getcwd(), 'venv')
activate_script = os.path.join(venv_dir, 'Scripts', 'activate.bat')

# Creación del entorno virtual
if not os.path.exists(activate_script):
    print("No se encontró el entorno virtual. Creándolo...")
    subprocess.run([sys.executable, "-m", "venv", "venv"])

# Instalación de dependencias
if os.path.exists("requirements.txt"):
    subprocess.run([os.path.join(venv_dir, 'Scripts', 'pip.exe'), 'install', '-r', 'requirements.txt'])

# Ejecución de la aplicación
subprocess.run([os.path.join(venv_dir, 'Scripts', 'python.exe'), 'app.py'])