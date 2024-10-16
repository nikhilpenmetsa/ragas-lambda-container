import boto3

#a2i_runtime_client = boto3.client('sagemaker-a2i-runtime')

a2i_runtime_client = boto3.Session(profile_name='hub-account').client('sagemaker-a2i-runtime')

response = a2i_runtime_client.start_human_loop(
    HumanLoopName='test-loop',
    FlowDefinitionArn='arn:aws:sagemaker:us-east-1:882641078759:flow-definition/test2',
    HumanLoopInput={
        'InputContent': '{"InputContent": {\"prompt\":\"What is the answer?\"}}'    
    },
    DataAttributes={
        'ContentClassifiers': [
            'FreeOfPersonallyIdentifiableInformation'
        ]
    }
)

print(response)


# import json
# import boto3
# from botocore.exceptions import ClientError

# eval_results = [
#     {'gt_id': 1, 'faithfulness': 1.0000, 'answer_relevancy': 0.0000, 'context_recall': 1.0000, 'context_precision': 0.0000},
#     {'gt_id': 2, 'faithfulness': 1.0000, 'answer_relevancy': 0.8602, 'context_recall': 1.0000, 'context_precision': 0.4778}
# ]

# def get_ssm_parameter(parameter_name):
#     ssm_client = boto3.Session(profile_name='hub-account').client('ssm')
#     #ssm_client = boto3.client('ssm')
    
#     try:
#         response = ssm_client.get_parameter(
#             Name=parameter_name,
#             WithDecryption=True  # Set to True if it's a SecureString
#         )
#         value_string = response['Parameter']['Value']
#         parameter_dict = json.loads(value_string)
#         return parameter_dict
   
#     except ClientError as e:
#         print(f"An error occurred: {e}")
#         return None

# #app_eval_threshold_metrics = os.environ.get('AppGenAIEvalThresholdMetrics')
# app_eval_threshold_metrics = "/AppGenAIEvalThresholdMetrics/blog_app1"
# threshold_metrics = get_ssm_parameter(app_eval_threshold_metrics)
# print("threshold_metrics: ", threshold_metrics)
# #threshold_metrics = {'faithfulness': 0.8, 'answer_relevancy': 0.7, 'context_recall': 0.6, 'context_precision': 0.5}

# def check_all_metrics_pass_thresholds(eval_results, threshold_metrics):
#     all_metrics_passed = True
#     for result in eval_results:
#         gt_id = result.get('gt_id', 'Unknown')  # Get the gt_id, or 'Unknown' if it doesn't exist
#         result_metrics = {k: v for k, v in result.items() if k != 'gt_id'}

#         for metric, threshold in threshold_metrics.items():
#             if metric not in result_metrics:
#                 print(f"Warning: Metric '{metric}' not found in evaluation result (gt_id: {gt_id})")
#                 all_metrics_passed = False
#             elif result_metrics[metric] < threshold:
#                 print(f"Metric '{metric}' failed: {result_metrics[metric]} < {threshold} (gt_id: {gt_id})")
#                 all_metrics_passed = False
#     return all_metrics_passed

# # Usage
# all_metrics_passed = check_all_metrics_pass_thresholds(eval_results, threshold_metrics)
# if all_metrics_passed:
#     print("All metrics passed their thresholds")
# else:
#     print("Some metrics failed to meet their thresholds")


# # core_eval_results = {'faithfulness': 0.7500, 'answer_relevancy': 0.0000, 'context_recall': 0.0000, 'context_precision': 0.0000}
# # print(core_eval_results)

# # core_eval_results['gt_id'] = 'asss'
# # print(core_eval_results)
