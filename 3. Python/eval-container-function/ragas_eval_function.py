import json
from evaluation import KnowledgeBasesEvaluations
from observability import BedrockLogs
from config import (
    REGION, FIREHOSE_NAME, CRAWLER_NAME, MODEL_ARN, KB_ID, EXPERIMENT_DESCRIPTION,
    APPLICATION_NAME, CUSTOM_TAG, GUARDRAIL_ID, GUARDRAIL_VERSION,
    MAX_TOKENS, TEMPERATURE, TOP_P, MODEL_ID_EVAL, MODEL_ID_GEN
)
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    answer_similarity,
    context_precision
)

bedrock_logs = BedrockLogs(delivery_stream_name=FIREHOSE_NAME, 
                            experiment_id=EXPERIMENT_DESCRIPTION)
metrics = [faithfulness,
            answer_relevancy,
            context_recall,
            answer_similarity,
            context_precision]

# Dummy question, you should use your questions related to your Knowledge bases
questions = [
    "Explain the significant judgments and estimates involved in the Company's lease accounting policies, as mentioned in the context information."
]

# Dummy ground truth answers, you should use your ground truth created by domain subject matter expert
ground_truths = [
    "The significant judgments and estimates involved in the Company's lease accounting policies, as mentioned in the context information, are:\n\n1. Determining whether a contract contains a lease, which requires evaluating if the Company has the right to control the use of an identified asset for a period of time in exchange for consideration.\n\n2. Allocating contract consideration between lease and non-lease components, particularly for arrangements involving multiple components, which involves applying judgment in determining the appropriate allocation methodology and standalone prices for each component.\n\n3. Determining the lease term, which involves assessing the likelihood of exercising renewal or termination options.\n\n4. Determining the incremental borrowing rate used to measure lease liabilities."
]


@bedrock_logs.watch(call_type='RAG-Evaluation')
def test_function(application_metadata):
    question, ground_truth = application_metadata['question'], application_metadata['ground_truth']
    results = {}
    kb_evaluate = KnowledgeBasesEvaluations(model_id_eval=MODEL_ID_EVAL, 
                          model_id_generation=MODEL_ID_GEN, 
                          metrics=metrics,
                          questions=question, 
                          ground_truth=ground_truth, KB_ID=KB_ID)
    # temp = kb_evaluate.prepare_evaluation_dataset()
    # print("Evaluation dataset prepared")
    # print(temp)
    kb_evaluate.evaluate() 
    results["evaluation_results"] = kb_evaluate.evaluation_results
    results["questions"] = kb_evaluate.questions
    results["ground_truth"] = kb_evaluate.ground_truth
    results["generated_answers"] = kb_evaluate.generated_answers
    results["contexts"] = kb_evaluate.contexts
    print(results["evaluation_results"])
    for key, value in results["evaluation_results"].items():
        print(f"{key}: {value}")
    return results

def lambda_handler(event, context):

    for question, ground_truth in zip(questions, ground_truths):
        
        application_metadata = {
            'question': [question],
            'ground_truth': [ground_truth],
            'experiment_description': EXPERIMENT_DESCRIPTION,
            'application_name': APPLICATION_NAME, 
            'custom_tag': CUSTOM_TAG,
            'max_token': MAX_TOKENS, 
            'temperature': TEMPERATURE, 
            'top_p':TOP_P,
            'kb_id': KB_ID
            }
        # execute the test and track it:
        test_function(application_metadata)

    # Return the results
    return {
        'statusCode': 200,
        'body': 'done evaluating...'
    }
