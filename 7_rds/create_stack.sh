#!/bin/bash

aws cloudformation create-stack --stack-name TK-RDS-Stack --template-body file://tk_rds_stack.yaml --parameters file://params.json --capabilities CAPABILITY_IAM --profile admin