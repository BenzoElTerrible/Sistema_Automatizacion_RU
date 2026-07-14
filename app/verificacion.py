import os
import subprocess
import datetime

# --- CONFIGURACIÓN ---
# Asegúrate de que esta ruta sea la que usas para correr tests
# Ejemplo: apps.repositorio (donde está tu tests.py)
RUTA_TESTS = "apps.repositorio.tests" 
LOG_FILE = "log.txt"

def logger(mensaje):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(mensaje + "\n")
    print(mensaje)

def ejecutar_prueba(clase, metodo, explicacion, pasos):
    test_path = f"{RUTA_TESTS}.{clase}.{metodo}"
    
    logger(f"\n{'='*60}")
    logger(f"🧪 PRUEBA: {metodo}")
    logger(f"   OBJETIVO: {explicacion}")
    logger(f"   PASOS:")
    for i, paso in enumerate(pasos, 1):
        logger(f"     {i}. {paso}")
    logger(f"{'-'*60}")

    # Ejecutar el comando de Django
    comando = ["python", "manage.py", "test", test_path, "--noinput", "-v", "1"]
    proceso = subprocess.run(comando, capture_output=True, text=True)

    if proceso.returncode == 0:
        logger("✅ RESULTADO: Exitosa. La lógica funciona según lo esperado.")
    else:
        logger("❌ RESULTADO: Fallida. Se detectó una inconsistencia.")
        logger("\n--- DETALLE TÉCNICO DEL ERROR ---")
        logger(proceso.stderr)
    logger(f"{'='*60}\n")

def iniciar_proceso():
    # Limpiar log anterior
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"INFORME DE EJECUCIÓN DE PRUEBAS - {datetime.datetime.now()}\n")
        f.write(f"Sistema: Sistema_Automatizacion_RU\n\n")

    print(f"Iniciando pruebas detalladas... el log se guardará en {LOG_FILE}\n")

    # --- DEFINICIÓN DE PRUEBAS BASADAS EN TU TESTS.PY ---

    # 1. Pruebas de Etiquetas
    ejecutar_prueba(
        "ObtenerEtiquetaTests", 
        "test_retorna_sigla_cuando_existe",
        "Verificar que si una Resolución tiene sigla (ej: 'ND'), el sistema use esa sigla.",
        ["Crear un objeto TipoRU con sigla 'ND'", "Llamar a la función obtener_etiqueta", "Validar que el resultado sea exactamente 'ND'"]
    )

    ejecutar_prueba(
        "ObtenerEtiquetaTests", 
        "test_elimina_tildes_del_nombre",
        "Asegurar que el sistema limpie acentos para evitar errores en nombres de archivos.",
        ["Crear nombre 'Modificación'", "Procesar string", "Verificar que la 'ó' se convirtió en 'o'"]
    )

    # 2. Pruebas de Validacion PDF
    ejecutar_prueba(
        "ValidacionPDFTests", 
        "test_archivo_sin_header_pdf_es_rechazado",
        "Seguridad: Impedir que archivos que no empiecen con '%PDF' sean subidos.",
        ["Instanciar un archivo falso .pdf", "Pasarlo por el Serializer", "Verificar que el sistema lance un error de validación"]
    )

    # 3. Pruebas de Vigencia
    ejecutar_prueba(
        "VigenciaDirectorTests", 
        "test_director_con_vencimiento_pasado_no_esta_vigente",
        "Control de fechas: Verificar que un director antiguo aparezca como NO vigente.",
        ["Crear nombramiento con fecha de 2024", "Llamar a esta_vigente()", "Confirmar que retorna False"]
    )

    print(f"\nPruebas finalizadas. Revisa el archivo '{LOG_FILE}' para ver este reporte completo.")

if __name__ == "__main__":
    iniciar_proceso()