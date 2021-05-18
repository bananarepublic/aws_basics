#!/bin/bash

aws cloudformation update-stack --stack-name TK-RDS-Stack --template-body file://tk_rds_stack.yaml --capabilities CAPABILITY_IAM --profile admin
