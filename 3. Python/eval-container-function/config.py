# # Configure the following values to be used in the example notebooks or, update these based on your implementation
REGION = "us-east-1"
FIREHOSE_NAME = "observability-882641078759-firehose-"
CRAWLER_NAME = "observability-882641078759-glue-crawler-"
MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"
MODEL_ARN = f"arn:aws:bedrock:{REGION}::foundation-model/{MODEL_ID}"

# # Knowledge Base Configuration
KB_ID = "38BKVBCQXT"
APPLICATION_NAME = 'nikhil-app-1'

# Application Configuration
EXPERIMENT_ID = "nikhil-eval-experiment-1" # this can be your project name
EXPERIMENT_DESCRIPTION = "This is an example experiment"
CUSTOM_TAG = {"application_stage":"production",
              "cost-centre":"GenAI-Center",
              "other-custom-tag":"tag-value"}

MODEL_ID_EVAL = "anthropic.claude-3-haiku-20240307-v1:0"
MODEL_ID_GEN = f"{MODEL_ID}"
# # Retrieval and Generation Configuration
GUARDRAIL_ID = "9tonjtfmpx2y"
GUARDRAIL_VERSION = "1"
MAX_TOKENS = 250
TEMPERATURE = 0.01
TOP_P = 0.01

# # Agent 
# AGENT_ID = "<your-agent-id>"
# AGENT_ALIAS_ID = "<your-agent-alias-id>"
# AGENT_CONFIG = {'model_name': 'Claude 3.0 Sonnet', 
#                 'temperature': TEMPERATURE}

# # Agent Session:
# SESSION_ID = "<your-session-id>"
ENABLE_TRACE, END_SESSION = True, False