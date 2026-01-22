from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from db.mongodb import connect_to_mongo
from airflow.reminder_dags.notification_dag import send_reminder_message


def send_reminder_task():
    connect_to_mongo()
    send_reminder_message()

with DAG(
    dag_id="send_reminder_dag",
    start_date=datetime(2024, 1, 1),
    schedule_interval="* 10 * * 1-5",
    catchup=False,
    tags=["reminder", "slack"],
) as dag:

    send_reminder = PythonOperator(
        task_id="send_reminder",
        python_callable=send_reminder_task,
    )
