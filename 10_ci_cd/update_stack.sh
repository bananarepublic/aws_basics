#!/bin/bash

aws cloudformation update-stack --stack-name TK-CI-CD-Stack --template-body file://tk_ci_cd_stack.yaml --capabilities CAPABILITY_IAM --profile admin
