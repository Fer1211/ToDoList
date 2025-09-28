# 📝 ToDoList PRO en Python (Consola)

Un gestor de tareas en consola desarrollado en **Python 3**, utilizando **Programación Orientada a Objetos (POO)** y la librería **Rich** para una interfaz más elegante y visual en la terminal.

Este proyecto forma parte de mi portafolio personal y demuestra buenas prácticas de desarrollo, manejo de archivos, exportación de datos y organización limpia del código.

---

## 🚀 Características

- 📌 **Gestión completa de tareas**: agregar, mostrar, editar, buscar y eliminar.
- ✅ **Marcar tareas como completadas**.
- 🔀 **Ordenar tareas** por fecha de creación o prioridad.
- 🔎 **Búsqueda con resaltado de palabras clave**.
- 📊 **Estadísticas de progreso**: total, pendientes y completadas.
- 💾 **Persistencia de datos** en JSON y TXT.
- 🔙 **Historial de acciones (logging)** en `acciones.log`.
- 🎨 **Interfaz estilizada en consola** con Rich.
- 📤 **Exportar tareas** en JSON, TXT, CSV y Excel.
- ↩️ **Funcionalidad Undo/Redo**.

---

## 📂 Estructura del Proyecto

ToDoList-Pro
┣ 📜 todo_oop.py # Código principal
┣ 📜 tareas.json # Persistencia en JSON
┣ 📜 tareas.txt # Exportación en texto plano
┣ 📜 acciones.log # Historial de acciones
┣ 📜 README.md # Documentación en inglés

---

## 🛠️ Instalación

1️⃣ Clonar este repositorio:

```bash
git clone https://github.com/Fer1211/ToDoList.git
cd ToDoList
````
2️⃣ Instalar las dependencias necesarias:
```bash
pip install rich pandas
```

3️⃣ Ejecutar la aplicación:
```Terminal
python todo_oop.py
```

💡 Sobre el Proyecto

ToDoList PRO es un gestor de tareas completo en consola, que combina POO, manejo de archivos JSON/TXT, y una interfaz visual estilizada con Rich.
Está diseñado para practicar buenas prácticas de programación, modularidad, persistencia de datos y UX en terminal.

📚 Tecnologías

Python 3

Rich (visualización en consola)

Pandas (exportación a Excel)

JSON y CSV para persistencia y exportación de datos

🤝 Contribuciones y Sugerencias

¡Se aceptan sugerencias y mejoras!
Si tienes ideas, errores que reportar o quieres mejorar alguna funcionalidad, puedes abrir un Issue o hacer un Pull Request en este repositorio.
Tu aporte será bienvenido y ayudará a mejorar ToDoList PRO.
