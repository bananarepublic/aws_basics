#!/bin/bash

aws cloudformation update-stack --stack-name TK-Lambda-Stack --template-body file://tk_lambda_stack.yaml --capabilities CAPABILITY_IAM --profile admin
