from  pathlib import Path
import sys
project_root = Path(__file__).parents[2]
sys.path.append(str(project_root))
from airflow.utils.task_group import TaskGroup
from dags.operators import initialize_postgres_operator,initialize_load_dim_operator, \
                            initialize_load_fact_operator, initialize_load_transformation_operator
from dags.utils import create_table_task_configs, insert_to_dim_table_task_configs, \
                        insert_to_fact_table_task_configs, insert_to_transformation_table_task_configs




def create_database_schema(dag, schema):
    task_id = 'create_schema'
    conn_id = 'postgres-warehouse'
    sql_query = f"""
        CREATE SCHEMA IF NOT EXISTS {schema};
        SET search_path TO {schema}, public;
        """ 
    
    return initialize_postgres_operator(dag, task_id, conn_id, sql_query)





def create_table_group(dag):

    with TaskGroup('create_table_group') as group:
        create_tables_tasks = [initialize_postgres_operator(
            dag, table_name=table_name, postgres_conn_id='postgres-warehouse', sql_query=sql_query
        ) for table_name, sql_query in create_table_task_configs.items()]
    return group


def load_dimension_group(dag):
    with TaskGroup('load_dimension_group') as group:
            load_dim_tasks = [initialize_load_dim_operator(
                dag, topic=topic, table_name=table_name, append=False
            ) for table_name, topic in insert_to_dim_table_task_configs.items()]
    return group


def load_fact_group(dag):
    with TaskGroup('load_fact_group') as group:
            load_fact_tasks = [initialize_load_fact_operator(
                dag, topic=topic, table_name=table_name
            ) for table_name, topic in insert_to_fact_table_task_configs.items()]
    return group

        
def load_transformation_group(dag):
    with TaskGroup('load_transformation_group') as group:
        load_transformation_tasks = [initialize_load_transformation_operator(
            dag, topic=config['topic'], table_name=table_name, key=config['key']
        ) for table_name, config in insert_to_transformation_table_task_configs.items()]
    return group



