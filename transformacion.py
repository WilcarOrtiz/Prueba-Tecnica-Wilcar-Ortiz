"""
 LOGICA DE TRANSFORMACION
"""
import pandas as pd

# === FUNCIONES COMUNES
def estandarizar_texto(columnas, tabla):
    """
    Pasar todo a minusculas en columnas especificas
    """
    for col in columnas:
        tabla[col] = tabla[col].str.lower()
    return tabla

def unificar_productos(productos_data):
    """
    Anade un id_interno que identifica a los productos con la misma informacion base
    """
    products_df = pd.DataFrame(productos_data['data'])
    products_df['created_at'] = pd.to_datetime(products_df['createdAt'])
    products_df = products_df[['id', 'name','description', 'price', 'category', 'created_at']]
    products_df = estandarizar_texto(['name', 'description', 'category'], products_df)
    products_df['id_interno'] = products_df.groupby(['name', 'description', 'price', 'category']).ngroup() + 1
    products_df = products_df.rename(columns={'id': 'id_producto'})
    return products_df

def separar_productos_en_compra(purchases_data):
    """
    El array de productos los 'explotamos' para tener un registro x item dentro del array
    """
    purchases_df = pd.DataFrame(purchases_data['data'])
    purchases_df['purchase_date'] = pd.to_datetime(purchases_df['purchaseDate'])
    purchases_df = purchases_df[['id', 'status', 'creditCardNumber', 'creditCardType', 'purchaseDate', 'products']]
    # Explotar productos
    purchases_exploded = purchases_df.explode('products').reset_index(drop=True)
    products_normalized = pd.json_normalize(purchases_exploded['products'])
    products_normalized = products_normalized.rename(columns={'id': 'id_producto_compra', 'discount': 'discount'})
    purchases_final = pd.concat([purchases_exploded.drop(columns=['products']), products_normalized], axis=1)
    return purchases_final

def agrupar_y_calcular_totales(productos_df,purchases_df):
    """
    Agrupa los dos daaset en uno, mediante el campo comun, 
    posteriormente agrupa los productos de cada compra y cuenta 
    cuantas veces se compraron cada uno para calcula el total
    """
    df_relacionado = purchases_df.merge(
        productos_df,
        left_on='id_producto_compra',
        right_on='id_producto',
        how='left'
    )
    df = (df_relacionado.groupby(
        ['id', 'id_interno', 'name', 'price', 'discount'], as_index=False)
                 .agg({
                     'creditCardNumber': 'first',
                     'creditCardType': 'first',
                     'purchaseDate': 'first',
                     'status': 'first',
                    'name': 'count'
                    }).rename(columns={'name': 'quantity'})
                 )
    df['total'] = df['price'] * df['quantity'] * (1 - df['discount'] / 100)
    return df

def transformacion(productos_data, purchases_data):
    """
    Orquesta toda la logica de transformacion y generacion de las tablas con informacion a almacenar en AWS
    """
    productos_df = unificar_productos(productos_data)
    purchases_df = separar_productos_en_compra(purchases_data)
    dataset = agrupar_y_calcular_totales(productos_df, purchases_df)
    
    # PRODUCTS
    products = productos_df.drop_duplicates(subset=['id_interno'])
    products = products.drop("id_producto", axis=1)
    products = products.rename(columns={'id_interno': 'id'})
    # PURCHASES
    purchases = (
        dataset.groupby(['id', 'status', 'creditCardType', 'purchaseDate'], as_index=False)
        .agg({'total': 'sum'})
        .rename(columns={ 
                         'creditCardType': 'credit_card_type',
                         'purchaseDate': 'purchase_date'
                         })
        )
    # PURCHASES_PRODUCTS
    purchase_products = (
        dataset.groupby(['id', 'id_interno'], as_index=False)
        .agg({'quantity': 'sum'})
        .rename(columns={
            'id': 'purchase_id',
            'id_interno': 'product_id'
            })
        )
    return [products, purchases, purchase_products]
