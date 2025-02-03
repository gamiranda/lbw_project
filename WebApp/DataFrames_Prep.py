from pyspark.sql import SparkSession
from pyspark.sql.functions import concat, lit, lpad, substring, to_date, col, when
from pyspark.sql import functions as F

spark = SparkSession.builder \
        .appName("CSV API Reader - LBW") \
        .getOrCreate()

def process_data(data):

    data = data.withColumn("DTNASC_padded",
                    lpad(col("DTNASC"), 8, '0')).select(
                    "IDADEMAE", 
                    "RACACORMAE",
                    "CODMUNNASC",
                    "PESO",
                    # Optimized date transformation
                    to_date(
                        concat(
                            lpad(substring(col("DTNASC_padded"), 1, 2), 2, '0'),
                            lpad(substring(col("DTNASC_padded"), 3, 2), 2, '0'),
                            substring(col("DTNASC_padded"), 5, 4)
                        ),
                        'ddMMyyyy'
                    ).alias("DTNASC_padded")
                ).withColumn("UF", substring(col("CODMUNNASC"), 1, 2)
                ).withColumn("ANO", substring(col("DTNASC_padded"), 1, 4)
                ).select("IDADEMAE", "RACACORMAE", "DTNASC_padded", "UF", "ANO", "PESO")
                

    return data

def createRegionState(data):

    data = data.withColumn("REGIAO",
                            when(col("UF").isin([11, 12, 13, 14, 15, 16, 17]), "Norte")
                            .when(col("UF").isin([21, 22, 23, 24, 25, 26, 27, 28, 29]), "Nordeste")
                            .when(col("UF").isin([31, 32, 33, 35]), "Sudeste")
                            .when(col("UF").isin([41, 42, 43]), "Sul")
                            .when(col("UF").isin([50, 51, 52, 53]), "Centro Oeste")
                            .otherwise("NA")  # Default value if none of the conditions match
                        ).withColumn("ESTADO",
                            when(col("UF") == 12, "AC")
                            .when(col("UF") == 27, "AL")
                            .when(col("UF") == 16, "AP")
                            .when(col("UF") == 13, "AM")
                            .when(col("UF") == 29, "BA")
                            .when(col("UF") == 23, "CE")
                            .when(col("UF") == 53, "DF")
                            .when(col("UF") == 32, "ES")
                            .when(col("UF") == 52, "GO")
                            .when(col("UF") == 21, "MA")
                            .when(col("UF") == 51, "MT")
                            .when(col("UF") == 50, "MS")
                            .when(col("UF") == 31, "MG")
                            .when(col("UF") == 15, "PA")
                            .when(col("UF") == 25, "PB")
                            .when(col("UF") == 41, "PR")
                            .when(col("UF") == 26, "PE")
                            .when(col("UF") == 22, "PI")
                            .when(col("UF") == 24, "RN")
                            .when(col("UF") == 43, "RS")
                            .when(col("UF") == 33, "RJ")
                            .when(col("UF") == 11, "RO")
                            .when(col("UF") == 14, "RR")
                            .when(col("UF") == 42, "SC")
                            .when(col("UF") == 35, "SP")
                            .when(col("UF") == 28, "SE")
                            .when(col("UF") == 17, "TO")
                            .otherwise("NA")  # Default value if no condition matches
                        )

    return data

dt = spark.read.csv("C:/Users/Usuario/Desktop/GitHub/LWB_article/LBW_article/bases/SINASC_2011.csv",
                            header=True,  # Assumes the first row is a header
                            inferSchema=True,  # Automatically detect column types
                            sep=';')
dt = process_data(dt)
dt = createRegionState(dt)

for ano in range(12, 22):
    dt_aux = spark.read.csv("C:/Users/Usuario/Desktop/GitHub/LWB_article/LBW_article/bases/SINASC_20" + str(ano) + ".csv",
                            header=True,  # Assumes the first row is a header
                            inferSchema=True,  # Automatically detect column types
                            sep=';')
    dt_aux = process_data(dt_aux)
    dt_aux = createRegionState(dt_aux)

    dt = dt.union(dt_aux)

for ano in range(22, 24):
    dt_aux = spark.read.csv("C:/Users/Usuario/Desktop/GitHub/LWB_article/LBW_article/bases/DNOPEN" + str(ano) + ".csv",
                            header=True,  # Assumes the first row is a header
                            inferSchema=True,  # Automatically detect column types
                            sep=';')
    dt_aux = process_data(dt_aux)
    dt_aux = createRegionState(dt_aux)

    dt = dt.union(dt_aux)

##### Montando as bases de dados

####### Agrupado por Ano
dt_grouped = dt.withColumn('BAIXO_PESO', F.when(F.col('PESO') <= 2500, 1).otherwise(0)).groupBy('ANO') \
                    .agg(F.format_number(F.avg('BAIXO_PESO') * 100, 2).alias('AVG_BAIXO_PESO')) \
                    .orderBy('ANO', ascending=False)
dt_grouped = dt_grouped.toPandas()
dt_grouped.to_csv("C:/Users/Usuario/Desktop/GitHub/LWB_article/LBW_article/bases/dt_grouped_ANO.csv",sep=";",index=False)

####### Agrupado por Ano e Regiao
dt_grouped = dt.withColumn('BAIXO_PESO', F.when(F.col('PESO') <= 2500, 1).otherwise(0)).groupBy('ANO', 'REGIAO') \
            .agg(F.format_number(F.avg('BAIXO_PESO') * 100, 2).alias('AVG_BAIXO_PESO')) \
            .orderBy('REGIAO', ascending=False)
dt_grouped = dt_grouped.toPandas()
dt_grouped.to_csv("C:/Users/Usuario/Desktop/GitHub/LWB_article/LBW_article/bases/dt_grouped_ANO_REGIAO.csv",sep=";",index=False)

####### Agrupado por Ano e Estado
dt_grouped = dt.withColumn('BAIXO_PESO', F.when(F.col('PESO') <= 2500, 1).otherwise(0)).groupBy('ANO', 'ESTADO') \
            .agg(F.format_number(F.avg('BAIXO_PESO') * 100, 2).alias('AVG_BAIXO_PESO')) \
            .orderBy('ESTADO', ascending=False)
dt_grouped = dt_grouped.toPandas()
dt_grouped.to_csv("C:/Users/Usuario/Desktop/GitHub/LWB_article/LBW_article/bases/dt_grouped_ANO_ESTADO.csv",sep=";",index=False)