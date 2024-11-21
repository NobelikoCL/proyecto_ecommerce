===========================================
INSTRUCCIONES DE INSTALACIÓN - STOCK SMART
===========================================

1. REQUISITOS PREVIOS
--------------------
- Python 3.x instalado
- pip (gestor de paquetes de Python)
- Git instalado

2. CLONAR EL REPOSITORIO
------------------------
git clone https://github.com/NobelikoCL/proyecto_ecommerce.git
cd proyecto_ecommerce

3. CREAR Y ACTIVAR ENTORNO VIRTUAL
---------------------------------
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate

4. INSTALAR DEPENDENCIAS
-----------------------
pip install -r requirements.txt

5. CONFIGURAR LA BASE DE DATOS
-----------------------------
python manage.py makemigrations
python manage.py migrate

6. CREAR SUPERUSUARIO (OPCIONAL)
-------------------------------
python manage.py createsuperuser

7. INICIAR EL SERVIDOR
---------------------
python manage.py runserver

8. ACCEDER A LA APLICACIÓN
-------------------------
Abrir en el navegador: http://127.0.0.1:8000

===========================================
COMANDOS ÚTILES
===========================================

# Desactivar entorno virtual
deactivate

# Ver paquetes instalados
pip list

# Actualizar requirements.txt
pip freeze > requirements.txt

===========================================
SOLUCIÓN DE PROBLEMAS COMUNES
===========================================

1. Si el comando 'python' no funciona:
   Intentar con 'python3' en su lugar

2. Si hay error al activar venv:
   - Verificar que estás en el directorio correcto
   - Asegurarse de que Python está en el PATH del sistema
   - En Windows, ejecutar PowerShell como administrador

3. Si hay error con las dependencias:
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall

===========================================
CONTACTO Y SOPORTE
===========================================

Para soporte técnico:
Email: hernan.villanueva.gutierrez@outlook.com
GitHub: https://github.com/NobelikoCL

===========================================