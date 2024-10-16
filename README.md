# Run Ragas evaluation framework in an AWS Lambda function

Ragas evaluation framework requires langchain, datasets and few other libraries that are larger than 250MB. This size limitation prevents using Lambda layers or packaging lambda functions. Code and instructions in this repostory show how to package these libraries and the function as a container image.

This repository packages code from a notebook (https://github.com/aws-samples/amazon-bedrock-samples/blob/main/evaluation-and-observability/3.%20Python/3.%20Example-Observability-for-RAG-Evaluation.ipynb) to run as an AWS Lambda function using a conatiner image.


## Usage
1. Install Docker
2. Clone this repository. Change directory to 3.\ Python/eval-container-function/
3. Build a docker image `docker build -t rag-eval-container-func .`
4. Get ECR credentials `aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-account-id.dkr.ecr.your-region.amazonaws.com`
5. Create an ECR repository for this image `aws ecr create-repository --repository-name rag-eval-container-function-repo --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE`
6. Tag image `docker tag rag-eval-container-func:latest your-account-id.dkr.ecr.your-region.amazonaws.com/rag-eval-container-function-repo:latest`
7. Push image to repository `docker push your-account-id.dkr.ecr.your-region.amazonaws.com/rag-eval-container-function-repo:latest`
8. Create a lambda function with Python 3.12 runtime. Select the container image. Set lambda function timeout to 3 minutes. Set memory to 512MB.
9. Grant the lambda function necessary fine grained access to Amazon Bedrock and Amazon Kinesis Firehose.
