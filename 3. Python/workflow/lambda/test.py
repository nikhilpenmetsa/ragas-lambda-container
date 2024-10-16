#Query a table in athena called "observability-882641078759-glue-database-"
import boto3
import pandas as pd

def query_athena(query):

    boto3_session = boto3.Session(profile_name='hub-account')
    # self.bedrock_client = boto3_session.client('bedrock-runtime')
    # self.bedrock_agent_client = boto3_session.client("bedrock-agent-runtime")


    athena = boto3_session.client('athena')
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': 'observability-882641078759-glue-database-'
        },
        ResultConfiguration={
            'OutputLocation': 's3://sym-eba-observability-882641078759/athena-results/'
        }
    )
    query_execution_id = response['QueryExecutionId']
    while True:
        query_status = athena.get_query_execution(QueryExecutionId=query_execution_id)['QueryExecution']['Status']['State']
        if query_status == 'SUCCEEDED':
            break
        elif query_status == 'FAILED':
            print("query_status", query_status)
            raise Exception(f"Athena query failed: {query_status['StateChangeReason']}")
    
    results = athena.get_query_results(QueryExecutionId=query_execution_id)
    columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    data = []
    for row in results['ResultSet']['Rows'][1:]:  # Skip header row
        data.append([field.get('VarCharValue', '') for field in row['Data']])

    df = pd.DataFrame(data, columns=columns)
    #print(df)

    #result = athena.get_query_results(QueryExecutionId=query_execution_id)['ResultSet']['Rows']
    #print(athena.get_query_results(QueryExecutionId=query_execution_id)['ResultSet'])
    return df

#query = 'SELECT * FROM "AwsDataCatalog"."observability-882641078759-glue-database-"."rag_evaluation" WHERE experiment_id like "EarningsRadarPro_benchmark_20241004_094024"'
#query = 'SELECT * FROM "AwsDataCatalog"."observability-882641078759-glue-database-"."rag_evaluation" limit 2'

query = '''
SELECT
    duration,
    input_log_temperature,
    output_log_evaluation_results_faithfulness,
    output_log_evaluation_results_answer_relevancy,
    output_log_evaluation_results_context_recall,
    output_log_evaluation_results_answer_similarity,
    output_log_evaluation_results_context_precision
FROM "AwsDataCatalog"."observability-882641078759-glue-database-"."rag_evaluation"
WHERE experiment_id like 'EarningsRadarPro_benchmark_20241004_094024';
'''
results_df = query_athena(query)

#Convert results_df to pandas dataframe
df = pd.DataFrame(results_df)
print(df)


#Convert to pandas dataframe

# df = pd.DataFrame(results_df[0:], columns=results_df[0])
# #print full dataframe
# pd.set_option('display.max_rows', None)
# print(df)
# #convert to csv
#results_df.to_csv('query_results.csv', index=False)

