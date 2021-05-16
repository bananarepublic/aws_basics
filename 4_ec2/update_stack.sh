#!/bin/bash

aws cloudformation update-stack --stack-name TK-EC2-Stack --template-body file://tk_ec2_stack.cf --profile admin
