import sys
sys.path.append('src')
from bd.models import *

print('Repartos con factura_id=11:')
try:
    repartos_11 = Reparto.select().where(Reparto.factura == 11)
    for r in repartos_11:
        print(f'  Reparto {r.id} apunta a factura {r.factura.folio_interno}')
except Exception as e:
    print(f'  Error: {e}')

print('\nFacturas con folio_interno=11:')
try:
    facturas_11 = Factura.select().where(Factura.folio_interno == 11)
    for f in facturas_11:
        print(f'  Factura {f.folio_interno}')
    if not facturas_11:
        print('  No hay facturas con folio_interno=11')
except Exception as e:
    print(f'  Error: {e}')

print('\nTodos los repartos y sus facturas:')
try:
    all_repartos = Reparto.select()
    for r in all_repartos:
        try:
            factura_id = r.factura.folio_interno if r.factura else 'NULL'
            print(f'  Reparto {r.id} -> Factura {factura_id}')
        except Exception as e:
            print(f'  Reparto {r.id} -> ERROR: {e}')
except Exception as e:
    print(f'  Error general: {e}')

db.close()
