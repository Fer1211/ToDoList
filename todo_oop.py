import json
import os
import csv
from datetime import datetime
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

# --- Clase Tarea ---
class Tarea:
    def __init__(self, descripcion: str, prioridad: str = "media"):
        self.descripcion = descripcion
        self.completada = False
        self.prioridad = prioridad.lower()
        self.fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def marcar_completada(self):
        self.completada = True

    def to_dict(self) -> Dict:
        return {
            "descripcion": self.descripcion,
            "completada": self.completada,
            "prioridad": self.prioridad,
            "fecha_creacion": self.fecha_creacion
        }

    @staticmethod
    def from_dict(data: Dict):
        tarea = Tarea(data["descripcion"], data.get("prioridad", "media"))
        tarea.completada = data.get("completada", False)
        tarea.fecha_creacion = data.get("fecha_creacion", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return tarea


# --- Clase Gestor ---
class GestorDeTareasPro:
    def __init__(self, archivo: str = "tareas.json"):
        self.archivo = archivo
        self.tareas: Dict[int, Tarea] = {}
        self.historial: List[Dict[int, Tarea]] = []
        self.rehacer_pila: List[Dict[int, Tarea]] = []
        self.contador_id = 1
        self.cargar_tareas()

    # --- Manejo de archivos ---
    def guardar_tareas(self):
        """Guarda todas las tareas en un archivo JSON como lista"""
        with open(self.archivo, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self.tareas.values()], f, ensure_ascii=False, indent=4)

    def cargar_tareas(self):
        """Carga las tareas desde un archivo JSON si existe"""
        if os.path.exists(self.archivo):
            with open(self.archivo, "r", encoding="utf-8") as f:
                data = json.load(f)

                if isinstance(data, dict):  # formato viejo
                    self.tareas = {int(k): Tarea.from_dict(v) for k, v in data.items()}
                    self.contador_id = max(self.tareas.keys(), default=0) + 1
                elif isinstance(data, list):  # formato nuevo (lista de tareas)
                    self.tareas = {i + 1: Tarea.from_dict(v) for i, v in enumerate(data)}
                    self.contador_id = len(self.tareas) + 1

    # --- Historial (Undo/Redo) ---
    def _guardar_estado(self):
        self.historial.append({k: Tarea.from_dict(v.to_dict()) for k, v in self.tareas.items()})
        self.rehacer_pila.clear()

    def undo(self):
        if self.historial:
            self.rehacer_pila.append({k: Tarea.from_dict(v.to_dict()) for k, v in self.tareas.items()})
            self.tareas = self.historial.pop()
            self.guardar_tareas()
            console.print("[yellow]↩️ Acción deshecha[/yellow]")
        else:
            console.print("[red]⚠️ No hay acciones para deshacer[/red]")

    def redo(self):
        if self.rehacer_pila:
            self.historial.append({k: Tarea.from_dict(v.to_dict()) for k, v in self.tareas.items()})
            self.tareas = self.rehacer_pila.pop()
            self.guardar_tareas()
            console.print("[yellow]↪️ Acción rehecha[/yellow]")
        else:
            console.print("[red]⚠️ No hay acciones para rehacer[/red]")

    # --- CRUD ---
    def agregar_tarea(self, descripcion: str, prioridad: str = "media"):
        self._guardar_estado()
        id_tarea = self.contador_id
        self.tareas[id_tarea] = Tarea(descripcion, prioridad)
        self.contador_id += 1
        self.guardar_tareas()
        self._log(f"Tarea agregada: {descripcion} (ID {id_tarea})")
        console.print(f"[green]✅ Tarea agregada con ID {id_tarea}[/green]")

    def completar_tarea(self, id_tarea: int):
        if id_tarea in self.tareas:
            self._guardar_estado()
            self.tareas[id_tarea].marcar_completada()
            self.guardar_tareas()
            self._log(f"Tarea completada (ID {id_tarea})")
            console.print(f"[cyan]✔️ Tarea {id_tarea} completada[/cyan]")
        else:
            console.print("[red]❌ ID no encontrado[/red]")

    def eliminar_tarea(self, id_tarea: int):
        if id_tarea in self.tareas:
            confirmar = input(f"⚠️ ¿Seguro que quieres eliminar la tarea {id_tarea}? (s/n): ").lower()
            if confirmar == "s":
                self._guardar_estado()
                desc = self.tareas[id_tarea].descripcion
                self.tareas.pop(id_tarea)
                self.guardar_tareas()
                self._log(f"Tarea eliminada: {desc} (ID {id_tarea})")
                console.print(f"[red]🗑️ Tarea {id_tarea} eliminada[/red]")
            else:
                console.print("[yellow]❌ Eliminación cancelada[/yellow]")
        else:
            console.print("[red]❌ ID no encontrado[/red]")

    def editar_tarea(self, id_tarea: int, nueva_desc: Optional[str] = None, nueva_prioridad: Optional[str] = None):
        if id_tarea in self.tareas:
            self._guardar_estado()
            if nueva_desc:
                self.tareas[id_tarea].descripcion = nueva_desc
            if nueva_prioridad:
                self.tareas[id_tarea].prioridad = nueva_prioridad.lower()
            self.guardar_tareas()
            self._log(f"Tarea editada (ID {id_tarea})")
            console.print(f"[blue]✏️ Tarea {id_tarea} actualizada[/blue]")
        else:
            console.print("[red]❌ ID no encontrado[/red]")

    # --- Mostrar ---
    def mostrar_tareas(self, filtro: Optional[str] = None, ordenar: str = "prioridad"):
        if not self.tareas:
            console.print("[bold red]⚠️ No hay tareas registradas[/bold red]")
            return

        table = Table(title="📋 Lista de Tareas")
        table.add_column("ID", justify="center", style="cyan")
        table.add_column("Descripción", style="magenta")
        table.add_column("Estado", style="green")
        table.add_column("Prioridad", style="yellow")
        table.add_column("Fecha creación", style="blue")

        for id_tarea, tarea in self.tareas_ordenadas(ordenar):
            if filtro == "pendientes" and tarea.completada:
                continue
            if filtro == "completadas" and not tarea.completada:
                continue
            estado = "✅" if tarea.completada else "⏳"
            table.add_row(str(id_tarea), tarea.descripcion, estado, tarea.prioridad, tarea.fecha_creacion)

        console.print(table)

    def tareas_ordenadas(self, criterio: str = "prioridad"):
        if criterio == "fecha":
            return sorted(self.tareas.items(), key=lambda x: x[1].fecha_creacion)
        else:  # por prioridad
            prioridad_valor = {"alta": 1, "media": 2, "baja": 3}
            return sorted(self.tareas.items(), key=lambda x: (prioridad_valor.get(x[1].prioridad, 2), x[0]))

    # --- Buscar ---
    def buscar_tarea(self, texto: str):
        resultados = {k: v for k, v in self.tareas.items() if texto.lower() in v.descripcion.lower()}
        if resultados:
            table = Table(title=f"🔍 Resultados de búsqueda: '{texto}'")
            table.add_column("ID", justify="center", style="cyan")
            table.add_column("Descripción", style="magenta")
            table.add_column("Estado", style="green")
            table.add_column("Prioridad", style="yellow")
            table.add_column("Fecha creación", style="blue")
            for id_tarea, tarea in resultados.items():
                estado = "✅" if tarea.completada else "⏳"
                # 🔥 Resaltar coincidencia en la descripción
                descripcion_resaltada = Text(tarea.descripcion)
                descripcion_resaltada.highlight_words([texto], style="bold yellow on red")
                table.add_row(str(id_tarea), descripcion_resaltada, estado, tarea.prioridad, tarea.fecha_creacion)
            console.print(table)
        else:
            console.print("[red]❌ No se encontraron coincidencias[/red]")

    # --- Estadísticas ---
    def mostrar_estadisticas(self):
        total = len(self.tareas)
        completadas = sum(1 for t in self.tareas.values() if t.completada)
        pendientes = total - completadas

        table = Table(title="📊 Estadísticas")
        table.add_column("Total", style="cyan")
        table.add_column("Pendientes", style="yellow")
        table.add_column("Completadas", style="green")
        table.add_row(str(total), str(pendientes), str(completadas))

        console.print(table)

    # --- Logging ---
    def _log(self, mensaje: str):
        with open("acciones.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - {mensaje}\n")

    # --- Exportar ---
    def exportar_tareas(self, filtro: Optional[str] = None, formato: str = "json", archivo: str = "export"):
        ordenadas = self.tareas_ordenadas()
        export_list = []
        for _, tarea in ordenadas:
            if filtro == "pendientes" and tarea.completada:
                continue
            if filtro == "completadas" and not tarea.completada:
                continue
            export_list.append(tarea.to_dict())

        if formato == "json":
            with open(f"{archivo}.json", "w", encoding="utf-8") as f:
                json.dump(export_list, f, ensure_ascii=False, indent=4)
            console.print(f"[green]✅ Exportadas {len(export_list)} tareas a {archivo}.json[/green]")
        elif formato == "txt":
            with open(f"{archivo}.txt", "w", encoding="utf-8") as f:
                for t in export_list:
                    estado = "Completada" if t["completada"] else "Pendiente"
                    f.write(f"{t['descripcion']} [{t['prioridad']}] - {estado}\n")
            console.print(f"[green]✅ Exportadas {len(export_list)} tareas a {archivo}.txt[/green]")
        elif formato == "csv":
            with open(f"{archivo}.csv", "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Descripción", "Completada", "Prioridad", "Fecha creación"])
                for t in export_list:
                    writer.writerow([t["descripcion"], "Sí" if t["completada"] else "No", t["prioridad"], t["fecha_creacion"]])
            console.print(f"[green]✅ Exportadas {len(export_list)} tareas a {archivo}.csv[/green]")
        elif formato == "excel":
            import pandas as pd
            data = [
                {
                    "Descripción": t["descripcion"],
                    "Completada": "Sí" if t["completada"] else "No",
                    "Prioridad": t["prioridad"],
                    "Fecha creación": t["fecha_creacion"]
                }
                for t in export_list
            ]
            df = pd.DataFrame(data)
            df.to_excel(f"{archivo}.xlsx", index=False)
            console.print(f"[green]✅ Exportadas {len(export_list)} tareas a {archivo}.xlsx[/green]")
        else:
            console.print("[red]❌ Formato no soportado (usa json/txt/csv/excel)[/red]")


# --- Menú ---
def menu():
    gestor = GestorDeTareasPro()

    while True:
        console.print("\n[bold cyan]=== Menú ToDoList Pro ===[/bold cyan]")
        console.print("1. ➕ Agregar tarea")
        console.print("2. ✔️ Completar tarea")
        console.print("3. 🗑️ Eliminar tarea")
        console.print("4. ✏️ Editar tarea")
        console.print("5. 📋 Mostrar todas las tareas")
        console.print("6. ⏳ Mostrar tareas pendientes")
        console.print("7. ✅ Mostrar tareas completadas")
        console.print("8. 🔍 Buscar tarea")
        console.print("9. 📊 Ver estadísticas")
        console.print("10. ↩️ Undo / ↪️ Redo")
        console.print("11. 📤 Exportar tareas (json/txt/csv/excel)")
        console.print("0. 🚪 Salir")

        opcion = input("Elige una opción: ")

        if opcion == "1":
            desc = input("Descripción de la tarea: ")
            prioridad = input("Prioridad (alta/media/baja): ").strip().lower()
            gestor.agregar_tarea(desc, prioridad)
        elif opcion == "2":
            id_tarea = int(input("ID de la tarea a completar: "))
            gestor.completar_tarea(id_tarea)
        elif opcion == "3":
            id_tarea = int(input("ID de la tarea a eliminar: "))
            gestor.eliminar_tarea(id_tarea)
        elif opcion == "4":
            console.print("[yellow]📋 Lista de tareas actuales:[/yellow]")
            gestor.mostrar_tareas()  # 👀 mostrar antes de pedir ID
            id_tarea = int(input("ID de la tarea a editar: "))
            nueva_desc = input("Nueva descripción (enter para no cambiar): ").strip()
            nueva_prioridad = input("Nueva prioridad (alta/media/baja, enter para no cambiar): ").strip().lower()
            gestor.editar_tarea(id_tarea, nueva_desc if nueva_desc else None, nueva_prioridad if nueva_prioridad else None)
        elif opcion == "5":
            ordenar = input("¿Ordenar por prioridad o fecha?: ").strip().lower()
            gestor.mostrar_tareas(ordenar=ordenar if ordenar in ["prioridad", "fecha"] else "prioridad")
        elif opcion == "6":
            gestor.mostrar_tareas(filtro="pendientes")
        elif opcion == "7":
            gestor.mostrar_tareas(filtro="completadas")
        elif opcion == "8":
            texto = input("Texto a buscar: ")
            gestor.buscar_tarea(texto)
        elif opcion == "9":
            gestor.mostrar_estadisticas()
        elif opcion == "10":
            accion = input("¿Deshacer (u) o Rehacer (r)?: ").lower()
            if accion == "u":
                gestor.undo()
            elif accion == "r":
                gestor.redo()
        elif opcion == "11":
            filtro = input("Filtrar (pendientes/completadas/todas): ").strip().lower()
            filtro = filtro if filtro in ["pendientes", "completadas"] else None
            formato = input("Formato (json/txt/csv/excel): ").strip().lower()
            archivo = input("Nombre archivo (sin extensión): ").strip() or "export"
            gestor.exportar_tareas(filtro=filtro, formato=formato, archivo=archivo)
        elif opcion == "0":
            console.print("[bold green]👋 Saliendo del programa...[/bold green]")
            break
        else:
            console.print("[red]❌ Opción inválida[/red]")


if __name__ == "__main__":
    menu()
