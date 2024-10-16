#!/bin/bash

# Load the variables from the setenv.sh file
source setenv.sh

uploadGroundTruthToBucket() {
    echo "Copying ground truth to a S3 bucket"

    GT_BUCKET_NAME=$(aws cloudformation describe-stacks \
        --profile "$PROFILE" \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].Outputs[?OutputKey==`GroundTruthBucketName`].OutputValue' \
        --output text)

    echo "Ground truth bucket name: $GT_BUCKET_NAME"
    aws --profile "$PROFILE" s3 cp ground_truth.csv s3://${GT_BUCKET_NAME}/ground_truth/
    echo "Copied ground truth  to s3://${GT_BUCKET_NAME}/ground_truth/"
    echo ""
}


ECR_REPO_URI=$(aws ecr describe-repositories --repository-names $ECR_REPO_NAME --profile "$PROFILE" --query 'repositories[0].repositoryUri' --output text 2>&1)
IMAGE_DIGEST=$(aws ecr describe-images \
    --profile "$PROFILE" \
  --repository-name rag-eval-repo \
  --image-ids imageTag=latest \
  --region us-east-1 \
  --query 'imageDetails[0].imageDigest' \
  --output text)


FIREHOSE_STREAM_NAME=$(aws cloudformation describe-stacks \
    --profile "$PROFILE" \
    --stack-name eval-prereq \
    --query 'Stacks[0].Outputs[?OutputKey==`FirehoseDeliveryStreamName`].OutputValue' \
    --output text)

GLUE_CRAWLER_NAME=$(aws cloudformation describe-stacks \
    --profile "$PROFILE" \
    --stack-name eval-prereq \
    --query 'Stacks[0].Outputs[?OutputKey==`GlueCrawlerName`].OutputValue' \
    --output text)


# Update the Stack
updateStack() {
    echo "Updating Stack: $STACK_NAME"
    update_output=$(aws cloudformation update-stack \
        --stack-name "$STACK_NAME" \
        --template-body file://../eval_pipeline.yaml \
        --parameters \
            ParameterKey=LambdaFunctionName,ParameterValue="Ragas-Eval-Function" \
            ParameterKey=StepFunctionName,ParameterValue="Eval-Workflow" \
            ParameterKey=LambdaImageUri,ParameterValue="${ECR_REPO_URI}@${IMAGE_DIGEST}" \
            ParameterKey=FirehoseDeliveryStreamName,ParameterValue="${FIREHOSE_STREAM_NAME}" \
            ParameterKey=GlueCrawlerName,ParameterValue="${GLUE_CRAWLER_NAME}" \
        --profile "$PROFILE" \
        --capabilities CAPABILITY_NAMED_IAM \
        --output json)

    if [ $? -eq 0 ]; then
        stack_id=$(echo "$update_output" | jq -r '.StackId')
        echo "Stack update initiated. Stack ID: $stack_id"
        echo "Waiting for stack update to complete..."
        aws cloudformation wait stack-update-complete --stack-name "$STACK_NAME" --profile "$PROFILE"
        echo "Stack update completed."
    else
        echo "Failed to initiate stack update. Error:"
        echo "$update_output"
        exit 1
    fi
}

# Check if the stack exists
checkStackExists() {
    aws cloudformation describe-stacks --stack-name "$STACK_NAME" --profile "$PROFILE" &> /dev/null
    return $?
}

# Print stack outputs
printStackOutputs() {
    echo "Stack Outputs:"
    outputs=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --profile "$PROFILE" --query 'Stacks[0].Outputs' --output json)
    
    if [ -z "$outputs" ] || [ "$outputs" == "null" ]; then
        echo "No outputs found for the stack."
    else
        echo "$outputs" | jq -c '.[]' | while read -r output; do
            key=$(echo "$output" | jq -r '.OutputKey')
            value=$(echo "$output" | jq -r '.OutputValue')
            echo "  $key: $value"
        done
    fi
}

if checkStackExists; then
    echo "Updating RAG Evaluation Pipeline Stack"
    updateStack
    uploadGroundTruthToBucket
    printStackOutputs
    echo "Completed updating RAG Evaluation Pipeline Stack"
else
    echo "Stack $STACK_NAME does not exist. Please create the stack first."
    exit 1
fi


