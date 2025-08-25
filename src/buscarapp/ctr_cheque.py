from cheque_form_control import FormPDF
from datetime import datetime
import sys
import os
from decimal import Decimal

# Agregar path para acceder a los modelos de BD
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from bd.models import Banco, OrdenCompra, Factura, Proveedor, Cheque as ChequeModel
    # Importar configuración para cuentas mayores
    sys.path.insert(0, os.path.join(parent_dir, '..', 'config'))
    from app_config import AppConfig
    # Importar TIPO_VALE desde solicitudapp
    from solicitudapp.config.app_config import AppConfig as SolicitudAppConfig
except ImportError:
    print("Error: No se pudieron importar los modelos de la base de datos")
    Banco = OrdenCompra = Factura = Proveedor = ChequeModel = None
    Banco = OrdenCompra = Factura = Proveedor = None
    AppConfig = None
    SolicitudAppConfig = None


def numero_a_letras(numero):
    """
    Convierte un número a letras en español con formato de centavos x/100
    
    Args:
        numero (float, int, str, Decimal): Número a convertir
    
    Returns:
        str: Número convertido a letras con formato "PESOS XX/100 MN"
    
    Ejemplo:
        numero_a_letras(1234.56) -> "MIL DOSCIENTOS TREINTA Y CUATRO PESOS 56/100 MN"
        numero_a_letras(100) -> "CIEN PESOS 00/100 MN"
        numero_a_letras(0.75) -> "CERO PESOS 75/100 MN"
    """
    try:
        # Convertir a Decimal para manejo preciso de decimales
        if isinstance(numero, str):
            # Limpiar string (remover comas, espacios, etc.)
            numero_limpio = numero.replace(',', '').replace(' ', '').strip()
            num = Decimal(numero_limpio)
        else:
            num = Decimal(str(numero))
        
        # Separar parte entera y centavos
        parte_entera = int(num)
        centavos = int((num - parte_entera) * 100)
        
        # Diccionarios para conversión
        unidades = ["", "UN", "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
        especiales = ["DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISÉIS", 
                     "DIECISIETE", "DIECIOCHO", "DIECINUEVE"]
        decenas = ["", "", "VEINTE", "TREINTA", "CUARENTA", "CINCUENTA", "SESENTA", 
                  "SETENTA", "OCHENTA", "NOVENTA"]
        centenas = ["", "CIENTO", "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS",
                   "SEISCIENTOS", "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]
        
        def convertir_grupo(num):
            """Convierte un grupo de 3 dígitos a letras"""
            if num == 0:
                return ""
            
            resultado = ""
            
            # Centenas
            if num >= 100:
                if num == 100:
                    resultado += "CIEN"
                else:
                    resultado += centenas[num // 100]
                num %= 100
                if num > 0:
                    resultado += " "
            
            # Decenas y unidades
            if num >= 20:
                resultado += decenas[num // 10]
                num %= 10
                if num > 0:
                    resultado += " Y " + unidades[num]
            elif num >= 10:
                resultado += especiales[num - 10]
            elif num > 0:
                resultado += unidades[num]
            
            return resultado
        
        def numero_completo_a_letras(numero):
            """Convierte un número completo a letras"""
            if numero == 0:
                return "CERO"
            
            grupos = []
            nombres_grupos = ["", "MIL", "MILLONES", "MIL MILLONES"]
            grupo_idx = 0
            
            while numero > 0 and grupo_idx < len(nombres_grupos):
                grupo = numero % 1000
                if grupo > 0:
                    grupo_letras = convertir_grupo(grupo)
                    
                    if grupo_idx == 1:  # Miles
                        if grupo == 1:
                            grupos.append("MIL")
                        else:
                            grupos.append(grupo_letras + " MIL")
                    elif grupo_idx == 2:  # Millones
                        if grupo == 1:
                            grupos.append("UN MILLÓN")
                        else:
                            grupos.append(grupo_letras + " MILLONES")
                    elif grupo_idx == 3:  # Mil millones
                        grupos.append(grupo_letras + " MIL MILLONES")
                    else:  # Unidades
                        grupos.append(grupo_letras)
                
                numero //= 1000
                grupo_idx += 1
            
            return " ".join(reversed(grupos))
        
        # Convertir parte entera
        if parte_entera == 0:
            letras_enteras = "CERO"
        else:
            letras_enteras = numero_completo_a_letras(parte_entera)
        
        # Formato final con centavos
        centavos_str = f"{centavos:02d}"  # Asegurar 2 dígitos
        resultado = f"{letras_enteras} PESOS {centavos_str}/100 MN"
        
        return resultado
        
    except (ValueError, TypeError, Exception) as e:
        # En caso de error, devolver formato por defecto
        return f"ERROR EN CONVERSIÓN: {str(numero)} PESOS 00/100 MN"


class Cheque:
    def __init__(self, factura, ruta):
        """
        Inicializa el objeto Cheque con una factura y la ruta de exportación
        
        Args:
            factura: Diccionario con los datos de la factura
            ruta: Ruta donde se guardará el PDF del cheque
        """
        self.factura = factura
        self.ruta = ruta
        
        # Inicializar formulario con datos de la factura
        self.form_info = self._llenar_formulario_factura()
    
    @classmethod
    def crear_multiple(cls, facturas, ruta, generar_reporte=True):
        """
        Método de clase para crear un cheque con múltiples facturas
        
        Args:
            facturas: Lista de diccionarios con datos de facturas
            ruta: Ruta donde se guardará el PDF del cheque
            generar_reporte: Si True, genera reporte PDF de las facturas (default: True)
            
        Returns:
            Cheque: Instancia de Cheque con facturas consolidadas
        """
        if not facturas:
            raise ValueError("La lista de facturas no puede estar vacía")
        
        # Generar reporte PDF de las facturas múltiples
        if generar_reporte and len(facturas) > 1:
            try:
                print(f"🔄 Iniciando generación de relación de vales para {len(facturas)} facturas...")
                
                # Importar el módulo de reportes
                import sys
                import os
                current_dir = os.path.dirname(os.path.abspath(__file__))
                sys.path.insert(0, current_dir)
                
                import ctr_reporte_chequemultiple
                generar_reporte_cheque_multiple = ctr_reporte_chequemultiple.generar_reporte_cheque_multiple
                
                # Generar nombre del reporte basado en la ruta del cheque
                import os
                nombre_cheque = os.path.splitext(os.path.basename(ruta))[0]
                
                # Crear directorio de reportes si no existe
                directorio_base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                directorio_reportes = os.path.join(directorio_base, "reportes")
                if not os.path.exists(directorio_reportes):
                    os.makedirs(directorio_reportes, exist_ok=True)
                
                # Ruta del reporte en la carpeta reportes
                ruta_reporte = os.path.join(directorio_reportes, f"{nombre_cheque} Relacion de Vales.pdf")
                
                print(f"📂 Directorio de reportes: {directorio_reportes}")
                print(f"📄 Nombre del cheque: {nombre_cheque}")
                print(f"📊 Ruta de relación: {ruta_reporte}")
                
                # Preparar información adicional del cheque
                info_cheque = {
                    'numero_cheque': nombre_cheque,
                    'proveedor': facturas[0].get('nombre_emisor', 'No especificado'),
                    'archivo_cheque': os.path.basename(ruta)
                }
                
                # Generar reporte
                resultado = generar_reporte_cheque_multiple(
                    facturas_data=facturas, 
                    ruta_pdf=ruta_reporte,
                    info_cheque=info_cheque,
                    abrir_automaticamente=False  # No abrir automáticamente para no interrumpir el flujo
                )
                
                print(f"✅ Relación de vales generada: {resultado}")
                existe = os.path.exists(resultado)
                print(f"📁 ¿Archivo existe? {'SÍ' if existe else 'NO'}")
                
                # MOSTRAR MENSAJE VISIBLE AL USUARIO
                if existe:
                    try:
                        import tkinter as tk
                        from tkinter import messagebox
                        
                        # Crear ventana temporal para mostrar mensaje
                        root = tk.Tk()
                        root.withdraw()  # Ocultar ventana principal
                        
                        mensaje = f"✅ REPORTE GENERADO EXITOSAMENTE\n\n"
                        mensaje += f"📄 Archivo: {os.path.basename(resultado)}\n"
                        mensaje += f"📂 Ubicación: {os.path.dirname(resultado)}\n"
                        mensaje += f"📁 Carpeta: reportes/\n\n"
                        mensaje += f"El reporte contiene {len(facturas)} facturas."
                        
                        messagebox.showinfo("Reporte de Vales Generado", mensaje)
                        root.destroy()
                    except Exception as e:
                        print(f"⚠️ No se pudo mostrar el mensaje gráfico: {e}")
                
            except Exception as e:
                print(f"❌ Error al generar relación de vales: {e}")
                import traceback
                traceback.print_exc()
                # Continuar sin fallar aunque el reporte tenga errores
        
        # Crear instancia temporal para usar el método de consolidación
        instancia_temp = cls(facturas[0], ruta)
        
        # Consolidar facturas
        factura_consolidada = instancia_temp._consolidar_facturas(facturas)
        
        # Crear instancia final con factura consolidada
        instancia_final = cls(factura_consolidada, ruta)
        
        # Guardar las facturas originales para poder asociarlas en la BD
        instancia_final._facturas_originales = facturas
        
        return instancia_final
    
    def _llenar_formulario_factura(self):
        """
        Llena el formulario con los datos de una sola factura
        
        Returns:
            dict: Diccionario con los campos del formulario llenos
        """
        # Obtener fecha actual en formato dd/mm/aa
        fecha_actual = datetime.now().strftime("%d/%m/%y")
        
        # Extraer datos básicos de la factura
        proveedor = self.factura.get('nombre_en_quiter', '')
        numero_vale = self.factura.get('no_vale', '')
        folio_factura = self.factura.get('folio', '')
        tipo_vale_codigo = self.factura.get('tipo', '')  # Código del tipo de vale (ej: "AL", "VM")
        total_factura = self.factura.get('total', 0)
        folio_interno = self.factura.get('folio_interno')
        departamento = self.factura.get('departamento', '')  # Agregar departamento
        
        # Obtener descripción del tipo de vale desde configuración
        tipo_vale = ""
        if tipo_vale_codigo and SolicitudAppConfig:
            tipo_vale = SolicitudAppConfig.TIPO_VALE.get(tipo_vale_codigo, tipo_vale_codigo)  # Si no encuentra el código, usar el código original
        elif tipo_vale_codigo:
            tipo_vale = tipo_vale_codigo  # Si no hay SolicitudAppConfig, usar el código original
        
        # Crear concepto: usar concepto consolidado si existe, sino crear normal
        if self.factura.get('concepto_consolidado'):
            concepto = self.factura.get('concepto_consolidado')
        else:
            # Obtener clase para incluir en el concepto
            clase_factura = self.factura.get('clase', '')
            if folio_factura:
                if clase_factura and clase_factura.lower() != 'vacio':
                    concepto = f"FACTURA {folio_factura} {clase_factura}"
                else:
                    concepto = f"FACTURA {folio_factura}"
            else:
                concepto = "FACTURA"
        
        # Crear campo Costos: debe mostrar el TIPO de vale, no el número
        campo_costos = ""
        if self.factura.get('vales_consolidados'):
            # Cheque múltiple: usar el tipo de vale del primer vale (factura base)
            if tipo_vale:
                campo_costos = tipo_vale
            elif tipo_vale_codigo:
                campo_costos = tipo_vale_codigo
            else:
                campo_costos = ""
        else:
            # Cheque individual: mostrar tipo de vale
            if tipo_vale:
                campo_costos = tipo_vale
            elif tipo_vale_codigo:
                campo_costos = tipo_vale_codigo
            else:
                campo_costos = ""
        
        # Inicializar valores por defecto
        importe_letras = ""
        cuenta_banco = ""
        banco_cuenta_mayor = ""  # Variable para cuenta_mayor del banco
        proveedor_cuenta_mayor = ""  # Variable para cuenta_mayor del proveedor
        codigo_proveedor = ""  # Variable para codigo_quiter del proveedor
        codigo_banco = ""  # Variable para código del banco
        nombre_proveedor = ""  # Variable para nombre del proveedor
        nombre_banco = ""  # Variable para nombre del banco
        
        try:
            # Obtener datos de la orden de compra si existe
            if folio_interno and OrdenCompra:
                orden_compra = OrdenCompra.select().where(
                    OrdenCompra.factura == folio_interno
                ).first()
                
                if orden_compra:
                    importe_letras = orden_compra.importe_en_letras or ""
            
            # Si no hay importe en letras en la BD, generarlo automáticamente
            if not importe_letras and total_factura:
                importe_letras = self.convertir_numero_a_letras(total_factura)
            
            # Obtener cuenta_mayor y codigo_quiter del proveedor usando el RFC emisor
            if Proveedor and self.factura.get('rfc_emisor'):
                rfc_emisor = self.factura.get('rfc_emisor')
                
                proveedor_obj = Proveedor.select().where(
                    Proveedor.rfc == rfc_emisor
                ).first()
                
                if proveedor_obj:
                    if proveedor_obj.cuenta_mayor:
                        proveedor_cuenta_mayor = proveedor_obj.cuenta_mayor
                    if proveedor_obj.codigo_quiter:
                        codigo_proveedor = proveedor_obj.codigo_quiter
                    if proveedor_obj.nombre:
                        nombre_proveedor = proveedor_obj.nombre
                    # Usar nombre_en_quiter para el campo Orden del cheque si existe
                    if proveedor_obj.nombre_en_quiter:
                        proveedor = proveedor_obj.nombre_en_quiter
                    elif proveedor_obj.nombre:
                        proveedor = proveedor_obj.nombre
                else:
                    # Si no se encuentra el proveedor por RFC, usar nombre_emisor como fallback
                    if not proveedor:
                        proveedor = self.factura.get('nombre_emisor', '')
            
            # Obtener datos del banco BTC23
            if Banco:
                banco_btc23 = Banco.select().where(
                    Banco.codigo == "BTC23"
                ).first()
                
                if banco_btc23:
                    cuenta_banco = banco_btc23.cuenta or ""
                    banco_cuenta_mayor = banco_btc23.cuenta_mayor or ""  # Obtener cuenta_mayor del banco
                    codigo_banco = banco_btc23.codigo or ""  # Obtener código del banco
                    nombre_banco = banco_btc23.nombre or ""  # Obtener nombre del banco
                    
        except Exception as e:
            print(f"Error accediendo a la base de datos: {e}")
            # Si hay error y no tenemos proveedor, usar nombre_emisor como fallback
            if not proveedor:
                proveedor = self.factura.get('nombre_emisor', '')
            # Si hay error, generar importe en letras automáticamente
            if total_factura:
                importe_letras = self.convertir_numero_a_letras(total_factura)

        if total_factura:
                importe_letras = self.convertir_numero_a_letras(total_factura)

        # Fallback final: asegurar que proveedor tenga un valor
        if not proveedor:
            proveedor = self.factura.get('nombre_emisor', '')

        # Verificar si hay IVA trasladado para determinar qué cuentas incluir
        iva_trasladado = self.factura.get('iva_trasladado', 0)
        tiene_iva = bool(iva_trasladado and iva_trasladado > 0)

        # Construir campo Nombre con nombres correspondientes
        nombres_lista = []
        
        # Nombre del proveedor - usar el mismo nombre que aparece en Orden (proveedor = nombre_en_quiter o fallback)
        if proveedor:  # Usar la variable proveedor que ya tiene el nombre correcto (nombre_en_quiter o fallback)
            nombres_lista.append(proveedor)
        elif proveedor_cuenta_mayor:  # Solo si tiene cuenta_mayor pero no nombre
            nombres_lista.append("")  # Placeholder si no hay nombre
        
        # Nombre del banco
        if banco_cuenta_mayor and nombre_banco:
            nombres_lista.append(nombre_banco)
        elif banco_cuenta_mayor:
            nombres_lista.append("")  # Placeholder si no hay nombre
        
        # Nombres para cuentas IVA SOLO si hay IVA trasladado
        if tiene_iva and AppConfig:
            iva_deber = AppConfig.CUENTAS_MAYORES.get('Iva_Deber', '')
            iva_haber = AppConfig.CUENTAS_MAYORES.get('Iva_Haber', '')
            
            if iva_deber:
                # Para IVA Deber: proveedor (nombre_en_quiter) + "IVA ACREDITABLE"
                nombre_iva_deber = f"{proveedor}\nIVA ACREDITABLE" if proveedor else "IVA ACREDITABLE"
                nombres_lista.append(nombre_iva_deber)
            if iva_haber:
                # Para IVA Haber: "IVA PAGADO"
                nombres_lista.append("IVA PAGADO")
        
        # No limitar los nombres, incluir todos (especialmente la línea 4 con "IVA PAGADO")
        nombres_mayores = "\n\n\n".join(nombres_lista)

        # Construir string de cuentas mayores con todas las cuentas necesarias
        cuentas_lista = []
        
        # MODIFICADO: Usar cuenta_mayor de OrdenCompra en lugar del proveedor
        orden_cuenta_mayor = None
        
        # Buscar la OrdenCompra asociada a la factura
        if folio_interno and OrdenCompra:
            try:
                orden_compra = OrdenCompra.select().where(
                    OrdenCompra.factura == folio_interno
                ).first()
                
                if orden_compra and orden_compra.cuenta_mayor:
                    orden_cuenta_mayor = orden_compra.cuenta_mayor
                    print(f"🏦 DEBUG: Usando cuenta mayor de OrdenCompra: {orden_cuenta_mayor}")
                else:
                    print(f"🔍 DEBUG: No se encontró OrdenCompra o sin cuenta mayor para factura {folio_interno}")
            except Exception as e:
                print(f"Error obteniendo cuenta mayor de OrdenCompra: {e}")
        
        # SIEMPRE incluir cuenta de la orden o cuenta por defecto
        if orden_cuenta_mayor:
            cuentas_lista.append(str(orden_cuenta_mayor))
            print(f"✅ DEBUG: Agregada cuenta mayor de orden: {orden_cuenta_mayor}")
        else:
            # Si no hay cuenta_mayor en OrdenCompra, usar "23020000" en lugar de "1200"
            cuentas_lista.append("23020000")  # Cuenta por defecto modificada
            print(f"⚠️ DEBUG: Usando cuenta por defecto: xxxx0000")
        
        # Agregar cuenta de banco si existe
        if banco_cuenta_mayor:
            cuentas_lista.append(str(banco_cuenta_mayor))
        
        # Agregar cuentas IVA desde configuración SOLO si hay IVA trasladado
        if tiene_iva and AppConfig:
            iva_deber = AppConfig.CUENTAS_MAYORES.get('Iva_Deber', '')
            iva_haber = AppConfig.CUENTAS_MAYORES.get('Iva_Haber', '')
            
            
            if iva_haber:
                cuentas_lista.append(str(iva_haber))
            if iva_deber:
                cuentas_lista.append(str(iva_deber))
        
        # Construir string de subcuentas con códigos correspondientes
        subcuentas_lista = []
        
        # SIEMPRE incluir subcuenta del proveedor si tenemos codigo o nombre
        if codigo_proveedor:
            subcuentas_lista.append(str(codigo_proveedor))
        elif nombre_proveedor:  # Si tenemos proveedor pero no codigo, usar nombre truncado o por defecto
            # Usar una subcuenta por defecto o parte del nombre
            subcuentas_lista.append("PROV")  # Subcuenta por defecto
        elif nombre_proveedor:  # Si tenemos proveedor pero no codigo, usar subcuenta por defecto
            subcuentas_lista.append("")  # Placeholder si no hay código pero sí proveedor
        
        # Subcuenta del banco: usar código del banco
        if banco_cuenta_mayor and codigo_banco:
            subcuentas_lista.append(str(codigo_banco))
        elif banco_cuenta_mayor:
            subcuentas_lista.append("")  # Placeholder si no hay código
        
        # Subcuentas IVA: usar codigo_quiter del proveedor también SOLO si hay IVA trasladado
        if tiene_iva and AppConfig:
            iva_deber = AppConfig.CUENTAS_MAYORES.get('Iva_Deber', '')
            iva_haber = AppConfig.CUENTAS_MAYORES.get('Iva_Haber', '')
            
            if iva_deber:
                subcuentas_lista.append(str(codigo_proveedor) if codigo_proveedor else "")
            if iva_haber:
                subcuentas_lista.append(str(codigo_proveedor) if codigo_proveedor else "")
        
        # Procesar cuentas: tomar primeros 4 dígitos y agregar 5 ceros
        cuentas_procesadas = []
        for cuenta in cuentas_lista:
            if len(cuenta) >= 4:
                primeros_4_digitos = cuenta[:4]  # Tomar primeros 4 dígitos
                cuenta_procesada = primeros_4_digitos + "00000"  # Agregar 5 ceros
                cuentas_procesadas.append(cuenta_procesada)
            else:
                # Si tiene menos de 4 dígitos, agregar ceros al inicio hasta tener 4, luego agregar 5 ceros
                cuenta_con_ceros = cuenta.zfill(4) + "00000"
                cuentas_procesadas.append(cuenta_con_ceros)
        
        # Procesar subcuentas: mantener valores originales sin transformaciones
        # Limitar a 2 subcuentas si no hay IVA, 3 si hay IVA
        limite_subcuentas = 2 if not tiene_iva else 3
        subcuentas_procesadas = []
        for subcuenta in subcuentas_lista[:limite_subcuentas]:
            if subcuenta:
                subcuentas_procesadas.append(str(subcuenta))
            else:
                # Si no hay subcuenta, agregar string vacío
                subcuentas_procesadas.append("")
        
        # Función para contar renglones que ocupa un nombre
        def contar_renglones_nombre(nombre, ancho_linea=25):
            """
            Cuenta cuántos renglones ocupará un nombre
            considerando el ancho de línea y ajuste de palabras
            
            Args:
                nombre (str): Nombre a analizar
                ancho_linea (int): Ancho máximo de caracteres por línea
                
            Returns:
                int: Número de renglones que ocupará el nombre
            """
            if not nombre or not nombre.strip():
                return 1  # Nombre vacío ocupa 1 renglón
            
            # Dividir el nombre en palabras
            palabras = str(nombre).strip().split()
            
            if not palabras:
                return 1
            
            renglones = 1
            longitud_renglon_actual = 0
            
            for i, palabra in enumerate(palabras):
                # Longitud que tendría si agregamos esta palabra
                longitud_con_palabra = longitud_renglon_actual
                
                # Si no es la primera palabra del renglón, agregar espacio
                if longitud_renglon_actual > 0:
                    longitud_con_palabra += 1  # espacio
                
                longitud_con_palabra += len(palabra)
                
                # Si excede el ancho, la palabra va al siguiente renglón
                if longitud_con_palabra > ancho_linea and longitud_renglon_actual > 0:
                    renglones += 1
                    longitud_renglon_actual = len(palabra)
                else:
                    longitud_renglon_actual = longitud_con_palabra
            
            return renglones
        
        # Construir campos Cuenta y subcuenta con alineación dinámica mejorada
        # Contar renglones del proveedor y banco para ajustar saltos de línea
        renglones_proveedor = contar_renglones_nombre(proveedor) if proveedor else 1
        renglones_banco = contar_renglones_nombre(nombre_banco) if nombre_banco else 1
        
        # Construir cuentas con separadores dinámicos individuales
        cuentas_con_separadores = []
        subcuentas_con_separadores = []
        
        # Saltos entre cuentas basados en renglones de nombres - DINÁMICO según IVA
        if tiene_iva:
            # CON IVA: 4 cuentas (proveedor, banco, IVA Deber, IVA Haber)
            saltos_cuenta = [
                renglones_proveedor + 2,  # Entre cuenta proveedor y banco
                renglones_banco + 3,      # Entre cuenta banco e IVA Deber
                renglones_proveedor + 3   # Entre IVA Deber e IVA Haber
            ]
        else:
            # SIN IVA: 2 cuentas (proveedor, banco)
            saltos_cuenta = [
                renglones_proveedor + 3   # Solo entre cuenta proveedor y banco
            ]
        
        # Procesar cuentas con saltos dinámicos
        for i in range(len(cuentas_procesadas)):
            cuenta = cuentas_procesadas[i]
            
            if i == 0:
                # Primera cuenta: sin saltos iniciales
                cuentas_con_separadores.append(cuenta)
            else:
                # Cuentas siguientes: con saltos según el array
                saltos = saltos_cuenta[i-1]
                cuentas_con_separadores.append("\n" * saltos + cuenta)
        
        # Procesar las 3 subcuentas con la lógica original mejorada
        for i in range(len(subcuentas_procesadas)):
            subcuenta = subcuentas_procesadas[i]
            
            if i == 0:
                # Primera subcuenta: sin saltos iniciales
                subcuentas_con_separadores.append(subcuenta)
            elif i == 1:
                # Segunda subcuenta: ajustar según si hay IVA o no
                if tiene_iva:
                    saltos = 2 + renglones_proveedor  # Con IVA: usar 2 (funcionaba bien)
                else:
                    saltos = 3 + renglones_proveedor  # Sin IVA: usar 3 (nuevo ajuste)
                subcuentas_con_separadores.append("\n" * saltos + subcuenta)
            elif i == 2:
                # Tercera subcuenta: 3 saltos base + renglones del banco
                saltos = 3 + renglones_banco
                subcuentas_con_separadores.append("\n" * saltos + subcuenta)
        
        # Unir todas las cuentas y subcuentas
        cuentas_mayores = "".join(cuentas_con_separadores)
        subcuentas_mayores = "".join(subcuentas_con_separadores)
        
        # Función para formatear números como moneda
        def formatear_moneda(valor):
            """Formatea un número como moneda con $ y separadores de miles"""
            if not valor:
                return ""
            try:
                # Convertir a float si es necesario
                if isinstance(valor, str):
                    valor = float(valor)
                # Formatear con 2 decimales y separadores de miles
                return f"${valor:,.2f}"
            except (ValueError, TypeError):
                return f"${valor}"
        
        # Construir campo Debe: factura.total seguido de muchos saltos de línea y luego factura.iva_trasladado
        debe_campo = formatear_moneda(total_factura) if total_factura else ""

        # Contar renglones del proveedor y banco para ajustar saltos de línea
        renglones_proveedor = contar_renglones_nombre(proveedor)
        renglones_banco = contar_renglones_nombre(nombre_banco)

        # Calcular saltos para el campo Debe (siempre, independiente de si hay IVA)
        saltos_debe = 10
        saltos_debe += (renglones_proveedor - 1) * 2  # +2 saltos por cada renglón adicional del proveedor
        saltos_debe += (renglones_banco - 1) * 2  # +2 saltos por cada renglón adicional del banco
        
        # Agregar IVA trasladado solo si existe
        if iva_trasladado:
            debe_campo += "\n" * saltos_debe + formatear_moneda(iva_trasladado)
        
        # Construir campo Haber: saltos de línea iniciales + factura.total + saltos + iva_trasladado + saltos finales
        haber_campo = ""
        if total_factura or iva_trasladado:
            # Calcular saltos iniciales según renglones del proveedor - ajustar según IVA
            if tiene_iva:
                saltos_haber_iniciales = 2 + renglones_proveedor  # Con IVA: usar 2 (funcionaba bien)
            else:
                saltos_haber_iniciales = 3 + renglones_proveedor  # Sin IVA: usar 3 (nuevo ajuste)
            saltos_haber = 3 + renglones_banco
            
            haber_campo = "\n" * saltos_haber_iniciales
            if total_factura:
                haber_campo += formatear_moneda(total_factura) + "\n" * saltos_haber  # Total + 3 saltos de línea
            if iva_trasladado:
                haber_campo += formatear_moneda(iva_trasladado)  # IVA trasladado 

        # Crear campo cheque: usar todos los vales si es múltiple, sino el individual
        campo_cheque = ""
        if self.factura.get('vales_consolidados'):
            # Cheque múltiple: mostrar todos los vales
            vales_lista = self.factura.get('vales_consolidados', [])
            if len(vales_lista) == 1:
                campo_cheque = str(vales_lista[0])
            else:
                # Para el campo cheque, usar formato más compacto
                campo_cheque = " ".join(vales_lista)
        else:
            # Cheque individual: usar el número de vale actual
            campo_cheque = str(numero_vale) if numero_vale else ""

        return {
            "Fecha1_af_date": fecha_actual,
            "Orden": proveedor,
            "Moneda": importe_letras,
            "cuenta": cuenta_banco,
            "cheque": campo_cheque,  # Campo cheque con vales individuales o múltiples
            "Concepto": concepto,
            "area": departamento,  # Campo departamento
            "Costos": campo_costos,  # Campo Costos con vales individuales o múltiples
            "subcuenta": subcuentas_mayores,  # Campo subcuentas con códigos
            "Debe": debe_campo,  # Campo Debe con total y luego IVA trasladado
            "Haber": haber_campo,  # Campo Haber con estructura específica
            "Cuenta": cuentas_mayores,
            "Nombre": nombres_mayores,  # Campo nombres con proveedores, banco e IVA
            "Parcial": "",
            "Cantidad": f"{total_factura:,.2f}" if total_factura else ""  # Campo Cantidad sin símbolo $ pero con formato de número
        }
    
    def convertir_numero_a_letras(self, numero):
        """
        Método de conveniencia para convertir número a letras usando la función global
        
        Args:
            numero: Número a convertir
            
        Returns:
            str: Número convertido a letras con formato x/100
        """
        return numero_a_letras(numero)
    
    def generar_cheque(self):
        """
        Genera el cheque PDF para una sola factura
        
        Returns:
            bool: True si se generó correctamente, False en caso contrario
        """
        try:
            # Crear instancia del formulario PDF
            form_pdf = FormPDF()
            
            # Llenar el formulario y guardarlo directamente
            form_pdf.rellenar(self.form_info, self.ruta)
            
            print(f"Cheque generado exitosamente en: {self.ruta}")
            return True
                
        except Exception as e:
            print(f"Error generando cheque: {str(e)}")
            return False

    def generar_multiple_cheques(self, facturas):
        """
        Método para generar cheques con múltiples facturas
        
        Args:
            facturas: Lista de facturas para el cheque múltiple
            
        Returns:
            bool: True si se generó correctamente, False en caso contrario
        """
        try:
            # Combinar todas las facturas en una factura consolidada
            factura_consolidada = self._consolidar_facturas(facturas)
            
            # Actualizar la factura del objeto con la consolidada
            self.factura = factura_consolidada
            
            # Regenerar el formulario con los datos consolidados
            self.form_info = self._llenar_formulario_factura()
            
            # Generar el cheque con los datos consolidados
            return self.generar_cheque()
            
        except Exception as e:
            print(f"Error generando cheque múltiple: {str(e)}")
            return False
    
    def _consolidar_facturas(self, facturas):
        """
        Consolida múltiples facturas en una sola para el cheque
        
        Args:
            facturas: Lista de diccionarios con datos de facturas
            
        Returns:
            dict: Factura consolidada con totales sumados
        """
        if not facturas:
            return {}
            
        # Usar la primera factura como base
        factura_base = facturas[0].copy()
        
        # Sumar totales e IVAs de todas las facturas
        total_consolidado = 0
        iva_consolidado = 0
        folios_facturas = set()  # Usar set para evitar duplicados
        vales_consolidados = []
        primera_clase_valida = ""  # Para almacenar la primera clase válida encontrada

        for factura in facturas:
            # Sumar total
            total_factura = factura.get('total', 0)
            if total_factura:
                total_consolidado += float(total_factura)
            
            # Sumar IVA trasladado
            iva_factura = factura.get('iva_trasladado', 0)
            if iva_factura:
                iva_consolidado += float(iva_factura)
            
            # Recopilar folios para el concepto (evitar duplicados)
            folio = factura.get('folio', '')
            if folio:
                folios_facturas.add(str(folio))  # add() para set en lugar de append()
            
            # Recopilar la primera clase válida (no vacía)
            if not primera_clase_valida:
                clase_factura = factura.get('clase', '')
                if clase_factura and clase_factura.lower() != 'vacio':
                    primera_clase_valida = clase_factura            # Recopilar números de vale para el campo Costos
            no_vale = factura.get('no_vale', '')
            if no_vale:
                vales_consolidados.append(str(no_vale))
        
        # Actualizar la factura base con los totales consolidados
        factura_base['total'] = total_consolidado
        factura_base['iva_trasladado'] = iva_consolidado if iva_consolidado > 0 else 0
        
        # Crear concepto con múltiples folios (convertir set a lista ordenada)
        folios_lista = sorted(list(folios_facturas))  # Convertir set a lista ordenada
        if folios_lista:
            if len(folios_lista) == 1:
                concepto_folios = f"FACTURA {folios_lista[0]}"
                # Agregar clase si existe
                if primera_clase_valida:
                    concepto_folios += f" {primera_clase_valida}"
            else:
                concepto_folios = f"FACTURAS {' '.join(folios_lista)}"
                # Agregar clase si existe
                if primera_clase_valida:
                    concepto_folios += f" {primera_clase_valida}"
        else:
            concepto_folios = f"FACTURAS ({len(facturas)} facturas)"
            # Agregar clase si existe
            if primera_clase_valida:
                concepto_folios += f" {primera_clase_valida}"

        # Actualizar concepto en la factura base
        factura_base['concepto_consolidado'] = concepto_folios
        
        # Agregar lista de vales consolidados para el campo Costos
        factura_base['vales_consolidados'] = vales_consolidados
        
        return factura_base

    def exportar(self):
        """
        Método de exportación principal que genera el cheque y lo guarda en la BD
        
        Returns:
            bool: True si se exportó correctamente, False en caso contrario
        """
        # Primero generar el PDF del cheque
        if self.generar_cheque():
            # Si el PDF se generó exitosamente, guardar en la base de datos
            try:
                self._guardar_cheque_en_bd()
                return True
            except Exception as e:
                print(f"Advertencia: PDF generado pero error guardando en BD: {e}")
                return True  # PDF ya se generó, no fallar por BD
        else:
            return False
    
    def _guardar_cheque_en_bd(self):
        """
        Guarda el registro del cheque en la base de datos
        """
        if not ChequeModel:
            print("Modelo Cheque no disponible, saltando guardado en BD")
            return
        
        try:
            from datetime import date
            
            # Obtener datos del formulario
            campo_cheque = self.form_info.get('cheque', '')
            proveedor_nombre = self.form_info.get('Orden', '')
            total_factura = self.factura.get('total', 0)
            
            # Buscar el proveedor (NO crear si no existe)
            proveedor_obj = None
            if proveedor_nombre and Proveedor:
                try:
                    # Buscar proveedor existente por nombre
                    proveedor_obj = Proveedor.get(Proveedor.nombre == proveedor_nombre)
                    print(f"✅ Proveedor encontrado: {proveedor_obj.nombre} (ID: {proveedor_obj.id})")
                except Proveedor.DoesNotExist:
                    try:
                        # Buscar por nombre_en_quiter
                        proveedor_obj = Proveedor.get(Proveedor.nombre_en_quiter == proveedor_nombre)
                        print(f"✅ Proveedor encontrado (nombre_en_quiter): {proveedor_obj.nombre} (ID: {proveedor_obj.id})")
                    except Proveedor.DoesNotExist:
                        # Si no se encuentra en ninguno de los dos campos, lanzar error
                        error_msg = (f"❌ Error: Proveedor '{proveedor_nombre}' no encontrado en la base de datos.\n\n"
                                   f"El proveedor debe estar registrado previamente en el sistema.\n"
                                   f"Verifique el nombre del proveedor o regístrelo antes de crear el cheque.")
                        print(f"❌ Proveedor no encontrado: {proveedor_nombre}")
                        raise ValueError(error_msg)
            elif not proveedor_nombre:
                error_msg = ("❌ Error: No se especificó un proveedor para este cheque.\n\n"
                           "Verifique que los datos del formulario estén completos.")
                print("❌ Nombre de proveedor vacío")
                raise ValueError(error_msg)
            else:
                error_msg = ("❌ Error: No se pudo acceder a la base de datos de proveedores.\n\n"
                           "Contacte al administrador del sistema.")
                print("❌ Modelo Proveedor no disponible")
                raise ValueError(error_msg)
            
            
            # Obtener folios de las facturas
            if self.factura.get('vales_consolidados'):
                # Cheque múltiple: obtener folios de todas las facturas (sin duplicados)
                folios_facturas = set()  # Usar set para evitar duplicados
                if hasattr(self, '_facturas_originales'):
                    for factura in self._facturas_originales:
                        folio = factura.get('folio', '')
                        if folio:
                            folios_facturas.add(str(folio))  # add() para set
                    folios_str = ' '.join(sorted(list(folios_facturas))) if folios_facturas else 'MULTIPLE'
                else:
                    folios_str = 'MULTIPLE'
            else:
                # Cheque individual: usar folio de la factura actual
                folios_str = str(self.factura.get('folio', ''))
            
            # Obtener código del banco (buscar BTC23 o usar por defecto)
            codigo_banco = ""
            try:
                if Banco:
                    banco_btc23 = Banco.select().where(Banco.codigo == "BTC23").first()
                    if banco_btc23:
                        codigo_banco = banco_btc23.codigo
                    else:
                        # Si no hay BTC23, usar el primer banco disponible
                        primer_banco = Banco.select().first()
                        if primer_banco:
                            codigo_banco = primer_banco.codigo
            except Exception as e:
                print(f"Error obteniendo banco: {e}")
                codigo_banco = "BTC23"  # Valor por defecto
            
            # Crear registro del cheque
            cheque_bd = ChequeModel.create(
                fecha=date.today(),
                vale=campo_cheque,
                folio=folios_str,
                proveedor=proveedor_obj,  # Usar el objeto Proveedor en lugar de la cadena
                monto=float(total_factura),  # Guardar como número, no como string formateado
                banco=codigo_banco
            )
            
            print(f"✅ Cheque guardado en BD: ID {cheque_bd.id}, Vale: {campo_cheque}, Proveedor: {proveedor_obj.nombre if proveedor_obj else 'Sin proveedor'}")
            
            # Si hay facturas, asociarlas al cheque
            self._asociar_facturas_a_cheque(cheque_bd)
            
        except Exception as e:
            print(f"Error guardando cheque en BD: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _asociar_facturas_a_cheque(self, cheque_bd):
        """
        Asocia las facturas al cheque en la base de datos
        
        Args:
            cheque_bd: Instancia del cheque creado en la BD
        """
        if not Factura:
            return
        
        try:
            # Obtener folio_interno de la factura base
            folio_interno = self.factura.get('folio_interno')
            
            if folio_interno:
                # Buscar la factura en la BD y asociarla al cheque
                try:
                    factura_bd = Factura.get(Factura.folio_interno == folio_interno)
                    factura_bd.cheque = cheque_bd
                    factura_bd.save()
                    print(f"✅ Factura {folio_interno} asociada al cheque {cheque_bd.id}")
                except Factura.DoesNotExist:
                    print(f"⚠️  Factura {folio_interno} no encontrada en BD")
            
            # Si es cheque múltiple y tenemos las facturas originales, asociar todas
            if hasattr(self, '_facturas_originales'):
                for factura_data in self._facturas_originales:
                    folio_interno_orig = factura_data.get('folio_interno')
                    if folio_interno_orig and folio_interno_orig != folio_interno:
                        try:
                            factura_bd = Factura.get(Factura.folio_interno == folio_interno_orig)
                            factura_bd.cheque = cheque_bd
                            factura_bd.save()
                            print(f"✅ Factura {folio_interno_orig} asociada al cheque {cheque_bd.id}")
                        except Factura.DoesNotExist:
                            print(f"⚠️  Factura {folio_interno_orig} no encontrada en BD")
            
        except Exception as e:
            print(f"Error asociando facturas al cheque: {e}")
    
    def get_datos_formulario(self):
        """
        Obtiene los datos del formulario para depuración
        
        Returns:
            dict: Diccionario con los datos del formulario
        """
        return self.form_info.copy()
    
    def actualizar_campo(self, campo, valor):
        """
        Actualiza un campo específico del formulario
        
        Args:
            campo: Nombre del campo a actualizar
            valor: Nuevo valor para el campo
        """
        if campo in self.form_info:
            self.form_info[campo] = valor
        else:
            print(f"Advertencia: Campo '{campo}' no existe en el formulario")