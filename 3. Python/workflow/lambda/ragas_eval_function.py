import json
import os
import boto3
import csv
import io
from botocore.exceptions import ClientError

from evaluation import KnowledgeBasesEvaluations
from observability import BedrockLogs

from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    answer_similarity,
    context_precision
)

FIREHOSE_NAME = os.environ.get('FirehoseDeliveryStreamName')
app_eval_config_params = os.environ.get('AppGenAIEvalConfigParams')
app_eval_threshold_metrics = os.environ.get('AppGenAIEvalThresholdMetrics')
app_groundtruth_bucket = os.environ.get('AppGroundTruthS3Bucket')


bedrock_logs = BedrockLogs(delivery_stream_name=FIREHOSE_NAME)

metrics = [faithfulness,
            answer_relevancy,
            context_recall,
            context_precision]

def get_ssm_parameter(parameter_name):
    #ssm_client = boto3.Session(profile_name='hub-account').client('ssm')
    ssm_client = boto3.client('ssm')
    
    try:
        response = ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=True  # Set to True if it's a SecureString
        )
        value_string = response['Parameter']['Value']
        parameter_dict = json.loads(value_string)
        return parameter_dict
   
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None


def read_ground_truth_from_s3(bucket_name, file_key, target_app_name):
    
    # boto3_session = boto3.Session(profile_name='hub-account')
    # s3 = boto3_session.client('s3')
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    
    content = response['Body'].read().decode('utf-8-sig')
    csv_file = io.StringIO(content)
    csv_reader = csv.DictReader(csv_file)
    
    gt_ids = []
    questions = []
    ground_truths = []
    
    for row in csv_reader:
        if row['app_name'] == target_app_name:
            gt_ids.append(row['gt_id'])
            questions.append(row['question'])
            ground_truths.append(row['ground_truth'])
    return gt_ids,questions, ground_truths

@bedrock_logs.watch(call_type='RAG-Evaluation')
def test_function(application_metadata):
    question, ground_truth = application_metadata['question'], application_metadata['ground_truth']
    results = {}
    kb_evaluate = KnowledgeBasesEvaluations(model_id_eval=application_metadata['judge_model_id'], 
                          model_id_generation=application_metadata['gen_model_id'], 
                          model_id_embed=application_metadata['embed_model_id'], 
                          num_retriever_results=application_metadata['num_retriever_results'], 
                          metrics=metrics,
                          questions=question, 
                          ground_truth=ground_truth, 
                          KB_ID=application_metadata['kb_id']
                        )
    # temp = kb_evaluate.prepare_evaluation_dataset()
    # print("Evaluation dataset prepared")
    # print(temp)
    kb_evaluate.evaluate() 
    results["evaluation_results"] = kb_evaluate.evaluation_results
    results["questions"] = kb_evaluate.questions
    results["ground_truth"] = kb_evaluate.ground_truth
    results["generated_answers"] = kb_evaluate.generated_answers
    results["contexts"] = kb_evaluate.contexts
    results["experiment_description"] = application_metadata['experiment_description']
    print(results["experiment_description"])
    print(results["evaluation_results"])
    for key, value in results["evaluation_results"].items():
        print(f"{key}: {value}")
    return results


def lambda_handler(event, context):
    
    print(event)
    
    if "runMode" not in event:
        raise ValueError("runMode is missing in the event")

    run_mode = event["runMode"]
    valid_modes = ("benchmark", "validation")

    if run_mode not in valid_modes:
        raise ValueError(f"Invalid runMode: {run_mode}. Expected 'benchmark' or 'validation'")


    experiment_description = event["execution_name"]
    application_name = event["application_name"]
    kb_id = event["kb_id"]
    if isinstance(kb_id, list):
            kb_id = kb_id[0] if kb_id else None  # Use the first element if the list is not empty, otherwise set to None
            
    gen_model_id = event["gen_model_id"]
    judge_model_id = event["judge_model_id"]
    embed_model_id = event["embed_model_id"]
    max_token = event["max_token"]
    temperature = event["temperature"]
    top_p = event["top_p"]
    num_retriever_results = event["num_retriever_results"]
    custom_tag = event["custom_tag"]
    experiment_param = event["experiment_param"]
    eval_results = []

    # S3 bucket and file information
    #bucket_name = 'rag-eval-pipeline-stack-groundtruth'
    file_key = 'ground_truth/ground_truth.csv'

    # Read questions and ground truths from S3
    gt_ids, questions, ground_truths = read_ground_truth_from_s3(app_groundtruth_bucket, file_key, application_name)

    eval_results = []

    for gt_id, question, ground_truth in zip(gt_ids, questions, ground_truths):
        
        application_metadata = {
            'question': [question],
            'ground_truth': [ground_truth],
            'experiment_description': experiment_description,
            'application_name': application_name, 
            'gen_model_id': gen_model_id,
            'judge_model_id': judge_model_id,
            'embed_model_id': embed_model_id,
            'num_retriever_results': num_retriever_results,
            'custom_tag': custom_tag,
            'max_token': max_token, 
            'temperature': temperature, 
            'top_p': top_p,
            'kb_id': kb_id
        }
        # execute the test and track it:
        eval_result = test_function(application_metadata)
        core_eval_results = eval_result["evaluation_results"]

        df = core_eval_results.scores.to_pandas()

        # Convert the DataFrame to a dictionary
        core_eval_results_dict = df.to_dict(orient='records')[0]
        core_eval_results_dict['gt_id'] = gt_id
        eval_results.append(core_eval_results_dict)

    print("eval_results: ", eval_results)

    #if runmode is validation then call get_ssm_parameter to get the threshold metrics
    if run_mode == "validation":
        return eval_results
        # threshold_metrics = get_ssm_parameter(app_eval_threshold_metrics)
        # print("threshold_metrics: ", threshold_metrics)
        # #compare the eval_results with the threshold metrics
        # #if any metric is less than the threshold, raise an exception
        # for metric, value in core_eval_results.items():
        #     if value < threshold_metrics[metric]:
        #         print(f"Metric {metric} value {value} is less than the threshold {threshold_metrics[metric]}")
    else:
        return {
            'statusCode': 200,
            'body': "Completed evaluating..."
        }

