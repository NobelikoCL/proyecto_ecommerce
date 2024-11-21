===========================================
GUÍA DE INSTALACIÓN DE REQUIREMENTS
===========================================

1. REQUISITOS PREVIOS
--------------------
- Tener Python instalado (versión 3.x)
- Tener pip instalado
- Tener Git instalado

2. PASOS DE INSTALACIÓN
----------------------

PASO 1: Clonar el repositorio
----------------------------
git clone https://github.com/NobelikoCL/proyecto_ecommerce.git
cd proyecto_ecommerce


PASO 2: Crear entorno virtual
---------------------------
# En Windows:
python -m venv venv

# En Linux/Mac:
python3 -m venv venv


PASO 3: Activar entorno virtual
-----------------------------
# En Windows (CMD):
venv\Scripts\activate

# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# En Linux/Mac:
source venv/bin/activate


PASO 4: Actualizar pip
--------------------
# En Windows:
python -m pip install --upgrade pip

# En Linux/Mac:
python3 -m pip install --upgrade pip


PASO 5: Instalar requirements
--------------------------
pip install -r requirements.txt


PASO 6: Verificar instalación
---------------------------
pip list


3. SOLUCIÓN DE PROBLEMAS COMUNES
-------------------------------

ERROR 1: "python no se reconoce como un comando..."
SOLUCIÓN: 
- Asegúrate de que Python está instalado
- Añade Python al PATH del sistema
- Reinicia la terminal

ERROR 2: "pip no se reconoce como un comando..."
SOLUCIÓN:
- Instala pip manualmente
- Verifica la instalación de Python
- Añade pip al PATH

ERROR 3: "Error al instalar algún paquete"
SOLUCIÓN:
- Intenta instalar el paquete individualmente:
  pip install nombre_del_paquete
- Verifica que tienes los permisos necesarios
- Actualiza pip e intenta nuevamente

ERROR 4: "PermissionError"
SOLUCIÓN:
- En Windows: Ejecuta PowerShell como administrador
- En Linux/Mac: Usa sudo (si es necesario)

4. VERIFICACIÓN FINAL
--------------------
1. El entorno virtual debe estar activado (verás (venv) en la terminal)
2. Todos los paquetes deben estar instalados (usa 'pip list')
3. No debe haber errores pendientes

5. COMANDOS ÚTILES
-----------------
# Ver versión de Python
python --version

# Ver versión de pip
pip --version

# Ver paquetes instalados
pip list

# Desactivar entorno virtual
deactivate

6. NOTAS IMPORTANTES
-------------------
- Siempre trabaja con el entorno virtual activado
- No instales paquetes globalmente
- Mantén actualizado el requirements.txt
- Si añades nuevos paquetes, actualiza requirements.txt:
  pip freeze > requirements.txt

===========================================
CONTACTO PARA SOPORTE
===========================================
Email: hernan.villanueva.gutierrez@outlook.com
GitHub: https://github.com/NobelikoCL