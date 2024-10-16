#!/bin/bash

# Load the variables from the setenv.sh file
source setenv.sh

FIREHOSE_STREAM_NAME = $(
    aws cloudformation describe-stacks \
        --stack-name eval-prereq \
        --query 'Stacks[0].Outputs[?OutputKey==`FirehoseDeliveryStreamName`].OutputValue' \
        --output text \
        --profile "$PROFILE"
)

# Deploy the Hub Stack
deployStack(){
    echo "Deploying Stack: $STACK_NAME"
    stack_id=$(aws cloudformation create-stack \
        --stack-name "$STACK_NAME" \
        --template-body file://../eval_pipeline.yaml \
        --parameters \
            ParameterKey=LambdaFunctionName,ParameterValue="Ragas-Eval-Function" \
            ParameterKey=StepFunctionName,ParameterValue="Eval-Workflow" \
            ParameterKey=FirehoseDeliveryStreamName,ParameterValue="$FIREHOSE_STREAM_NAME" \
        --profile "$PROFILE" \
        --capabilities CAPABILITY_NAMED_IAM \
        --query 'StackId' \
        --output text)

    echo "Waiting stack to be created..."
    aws cloudformation wait stack-create-complete --stack-name "$stack_id" --profile "$PROFILE"
    echo "Stack creation completed."
    echo ""
}

echo "Deploying RAG Evaluation Pipeline Stack"
echo ""
deployStack
echo "Completed deploying RAG Evaluation Pipeline Stack"