#!/bin/bash

aws cloudformation create-stack --stack-name TK-SNS-SQS-Stack --template-body file://tk_sns_sqs_stack.yaml --capabilities CAPABILITY_IAM --profile admin