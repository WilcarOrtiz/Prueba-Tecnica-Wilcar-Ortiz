"""
PIPELINE ETL
"""
import sys
from extraccion import extraccion_data
from transformacion import transformacion
from carga import cargar_AWS

def main():
    """
    FUNCION QUE ORQUESTA EL PIPELINE
    """
    try:
        print("1) EXTRACCION")
        productos_data = extraccion_data('products')
        purchases_data = extraccion_data('purchases')

        if not productos_data or not purchases_data:
            raise ValueError("No se pudieron extraer los datos correctamente")

        print("2) TRANSFORMACION")
        products, purchases, purchase_products = transformacion(
            productos_data, purchases_data)

        if any(df.empty for df in [products, purchases, purchase_products]):
            raise ValueError("Uno o más DataFrames transformados están vacíos")

        print("3) CARGA")
        cargar_AWS(products, purchases, purchase_products)
        print("Pipeline ETL completado corretamente")
    except Exception as e:
        print("Error durante la ejecución del pipeline:", e)
        sys.exit(1)
        
if __name__ == "__main__":
    main()
