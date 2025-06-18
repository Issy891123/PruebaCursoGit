from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pyspark.sql import SparkSession

def spark_job():
    spark = SparkSession.builder.appName("AirflowSparkExample").getOrCreate()
    df = spark.read.csv("/path/to/input.csv", header=True)
    df_processed = df.filter(df['value'] > 100)
    df_processed.write.csv("/path/to/output.csv", header=True)
    spark.stop()

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 10, 11),
    'retries': 1,
}

dag = DAG('spark_example_dag', default_args=default_args, schedule_interval='@daily')

spark_task = PythonOperator(
    task_id='run_spark_job',
    python_callable=spark_job,
    dag=dag,
)
